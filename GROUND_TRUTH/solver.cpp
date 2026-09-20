// GROUND_TRUTH/solver.cpp  --  3-row Chomp P-positions, streaming solver.
//
// Implements the recurrence of Brouwer, Horvath, Molnar-Saska, Szabo (2005),
// MISSION.md section 2.  f(q,r) is the unique p >= q such that (p,q,r) is a
// P-position, or a carried-forward stale value when no such p exists:
//
//   f(0,0) = 1
//   f(q,r) = f(q,q)                                  if r > q
//   f(q,r) = f(q-1,r)                                if f(q-1,r) < q     [STALE]
//   f(q,r) = mex {f(a,r) : a<q} u {f(q,b) : b<r}     otherwise
//
// mex is over the POSITIVE integers.
//
// Why this is not a table.  The naive table has O(n^2) cells and O(n^3) mex
// work: at r = 50000 that is ~1e13 cell visits and tens of GB.  Four
// structural facts collapse it to a single streaming pass.
//
//  1. Every column r settles by q ~ 1.5r.  It either goes STALE forever
//     (f(q,r) = c < q; the row has only finitely many P-positions) or f(q,r)-q
//     becomes exactly periodic.  A settled column answers f(q,r) for every
//     later q in O(1) from an O(period)-sized descriptor and needs no storage.
//  2. The mex at (q,r) needs only the current row {f(q,b) : b<r}, which we are
//     computing left to right anyway, and the column value SET {f(a,r) : a<q},
//     maintained incrementally as a bitset.  No cell is read twice, so the
//     table never has to exist.
//  3. The values missing from a column's value set below q are exactly the
//     stale constants of the dead columns beneath it.  Folding those into the
//     same bitset ("cov") makes it cover an unbroken prefix [1..q-1], so a
//     monotone pointer skips the whole low range in O(1) amortised.
//  4. Every live row value f(q,b) is >= q, so the row set lives in the window
//     [q, q+maxd].  Keeping it as an absolutely-indexed bitset lets the mex be
//     found by scanning cov|row 64 candidates at a time.
//
// Peak memory is (#live columns in flight) x O(r) bits -- a few hundred MB at
// r = 50000 rather than O(r^2).
//
// Build:  g++ -O2 -std=c++17 -o solver solver.cpp
//         cl /O2 /std:c++17 /EHsc solver.cpp
//
// This file is ground truth.  Sessions must not edit it; file a solver_bug
// claim with a reproducing input instead (MISSION.md section 6).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <chrono>
#if defined(_MSC_VER)
#include <intrin.h>
#endif

typedef uint64_t u64;
typedef uint32_t u32;
typedef int32_t  i32;
typedef uint8_t  u8;

static const int PMAX = 64;          // largest period the detector will find

static void fatal(const char *m, long long a = -1, long long b = -1) {
    std::fprintf(stderr, "solver: FATAL %s [%lld %lld]\n", m, a, b);
    std::exit(2);
}

#if defined(_MSC_VER)
static inline int ctz64(u64 x) { unsigned long i; _BitScanForward64(&i, x); return (int)i; }
#else
static inline int ctz64(u64 x) { return __builtin_ctzll(x); }
#endif

static inline bool bget(const u64 *w, u32 i) { return (w[i >> 6] >> (i & 63)) & 1ULL; }
static inline void bset(u64 *w, u32 i)       { w[i >> 6] |= 1ULL << (i & 63); }

enum ColState : u8 { UNBORN = 0, ACTIVE = 1, SETTLED = 2, STALE = 3 };

struct Col {
    u32  covbits  = 0;
    u32  covptr   = 0;         // largest m with [1..m] entirely inside cov
    u32  prev     = 0;         // f(q-1,r)
    u32  qmax     = 0;         // q at which we try to finalise this column
    u32  period   = 0;
    u32  Npre     = 0;         // preperiod N(r)
    u32  dconst   = 0;         // STALE: the carried constant
    u32  deathq   = 0;         // STALE: first q at which the carry kicked in
    u32  lastlive = 0;         // last q with a genuine P-position (f(q,r) >= q)
    u32  qend     = 0;         // q at which the column was finalised
    u32  extends  = 0;
    i32  dring[PMAX];          // d(q) indexed by q % PMAX
    i32  lastbad[PMAX + 1];    // (max q with d(q) != d(q+p)) + 1;  0 = never bad
    i32  dper[PMAX];           // SETTLED: d indexed by q % period
};

struct Solver {
    u32 R = 0, QGLOB = 0, maxval = 0, globbits = 0, win = 0;
    double alpha = 1.8;
    u32 margin = 600, confirmBase = 300;

    std::vector<Col>  col;
    std::vector<u8>   cstate;   // compact copy of state (scan-friendly)
    std::vector<u64*> cov;      // per-column bitset, freed on settle/death
    std::vector<u32>  rowstamp; // rowstamp[v]==q+1 <=> v in this q's row set
    std::vector<u64>  rowbits;  // same set, absolutely indexed, window [q,q+win]
    std::vector<u32>  diag;     // f(a,a)
    std::vector<u64>  global;   // {f(a,a):a<q} u {every stale constant so far}

    u64 cells = 0, words = 0, lowsteps = 0, ptrwords = 0, bcast = 0;
    u32 maxd = 0, unsettled = 0, maxext = 0, maxlow = 0;

    // qforce lets `row --qmax Q` sweep past the automatic horizon.  It has to
    // be known here: every array below is sized from QGLOB, so raising QGLOB
    // afterwards would run the row-set window off the end of its allocation.
    void init(u32 R_, double alpha_, u32 margin_, u32 confirm_, u32 qforce = 0) {
        R = R_; alpha = alpha_; margin = margin_; confirmBase = confirm_;
        QGLOB  = (u32)(alpha * (double)R) + margin + 16;
        if (qforce > QGLOB) QGLOB = qforce;
        win    = R + 256;                    // f(q,r) - q never exceeds ~0.72 r
        maxval = QGLOB + win + 256;
        col.assign(R + 1, Col());
        cstate.assign(R + 1, UNBORN);
        cov.assign(R + 1, nullptr);
        rowstamp.assign(maxval + 2, 0);
        rowbits.assign((maxval + 128) / 64 + 2, 0ULL);
        diag.assign(R + 2, 0);
        globbits = 2 * R + 512;
        global.assign((globbits + 63) / 64, 0ULL);
    }
    ~Solver() { for (auto p : cov) std::free(p); }

    inline u32 colmax(u32 r)  const { return (u32)(alpha * (double)r) + margin; }
    inline u32 confirm(u32 r) const { u32 c = r / 4; return c < confirmBase ? confirmBase : c; }

    void birth(u32 r) {
        Col &c = col[r];
        c.qmax    = colmax(r);
        c.covbits = c.qmax + win + 64;
        if (c.covbits > maxval) c.covbits = maxval;
        u32 nw = (c.covbits + 63) / 64;
        u64 *p = (u64 *)std::calloc(nw, sizeof(u64));
        if (!p) fatal("out of memory allocating column", r);
        // {f(a,r) : a<r} = {f(a,a) : a<r} by the r>q branch, together with every
        // stale constant emitted so far -- which is exactly `global`.
        u32 gw = (u32)global.size();
        std::memcpy(p, global.data(), sizeof(u64) * (nw < gw ? nw : gw));
        cov[r] = p;
        c.covptr = 0;
        c.prev   = (r == 0) ? 0 : diag[r - 1];   // f(r-1,r) = f(r-1,r-1)
        cstate[r] = ACTIVE;
        for (int p2 = 0; p2 <= PMAX; ++p2) c.lastbad[p2] = 0;
        for (int p2 = 0; p2 < PMAX; ++p2) { c.dring[p2] = INT32_MIN; c.dper[p2] = 0; }
    }

    void release(u32 r) { std::free(cov[r]); cov[r] = nullptr; col[r].covbits = 0; }

    void go_stale(u32 r, u32 q) {
        Col &c = col[r];
        cstate[r] = STALE;
        c.dconst = c.prev; c.deathq = q; c.qend = q;
        release(r);
        if (c.dconst >= globbits) fatal("stale constant past global bitset", r, c.dconst);
        bset(global.data(), c.dconst);
        // Every column above r now sees this constant in its own value set.
        u32 hi = (q < R) ? q : R;
        for (u32 r2 = r + 1; r2 <= hi; ++r2) {
            if (cstate[r2] != ACTIVE) continue;
            ++bcast;
            if (c.dconst < col[r2].covbits) bset(cov[r2], c.dconst);
        }
    }

    void settle(u32 r, u32 q) {
        Col &c = col[r];
        u32 need = confirm(r);
        for (u32 p = 1; p <= PMAX; ++p) {
            i32 lb = c.lastbad[p];
            u32 from = (lb == 0) ? r : (u32)lb;         // N_p = lastbad + 1
            if (q >= from + need) {
                c.period = p; c.Npre = from; c.qend = q;
                for (u32 j = 0; j < p; ++j) {
                    u32 qq = q - j;
                    c.dper[qq % p] = c.dring[qq % PMAX];
                }
                cstate[r] = SETTLED;
                release(r);
                return;
            }
        }
        // Nothing confirmed yet: push the horizon out and look again later.
        if (++c.extends > 12) fatal("column never settles", r, q);
        if (c.extends > maxext) maxext = c.extends;
        c.qmax = q + q / 2 + 1024;
        u32 nb = c.qmax + win + 64;
        if (nb > maxval) fatal("column grew past maxval", r, nb);
        if (nb > c.covbits) {
            u32 nw = (nb + 63) / 64, ow = (c.covbits + 63) / 64;
            u64 *p = (u64 *)std::realloc(cov[r], nw * sizeof(u64));
            if (!p) fatal("out of memory growing column", r);
            std::memset(p + ow, 0, (nw - ow) * sizeof(u64));
            cov[r] = p; c.covbits = nb;
        }
        if (c.qmax > QGLOB) QGLOB = c.qmax;
    }

    inline u32 eval_settled(const Col &c, u32 q) const {
        return q + (u32)c.dper[q % c.period];
    }

    // mex over cov[r] u rowset, exploiting the monotone prefix pointer.
    u32 mex(u32 r, u32 q) {
        Col &c = col[r];
        const u64 *cb = cov[r];
        // (1) push the prefix pointer over the run of ones that begins at it
        u32 i = c.covptr + 1;
        while (i < c.covbits) {
            u32 w = i >> 6;
            u64 z = ~cb[w] & (~0ULL << (i & 63));
            ++ptrwords;
            if (z) { i = (w << 6) + (u32)ctz64(z); break; }
            i = (w + 1) << 6;
        }
        if (i >= c.covbits) fatal("prefix scan ran off the bitset", r, q);
        c.covptr = i - 1;
        // (2) low region (values < q).  Non-empty only while some column below
        // r is in its very last live step, so this is O(1) in practice.
        u32 lo = 0;
        while (i < q && (bget(cb, i) || rowstamp[i] == q + 1)) { ++i; ++lo; }
        if (lo > maxlow) maxlow = lo;
        lowsteps += lo;
        if (i < q) return i;
        // (3) window region: scan cov|row 64 candidates at a time
        while (i < c.covbits) {
            u32 w = i >> 6;
            u64 z = ~(cb[w] | rowbits[w]) & (~0ULL << (i & 63));
            ++words;
            if (z) return (w << 6) + (u32)ctz64(z);
            i = (w + 1) << 6;
        }
        fatal("mex ran off the bitset", r, q);
        return 0;
    }

    template <class F>
    void sweep(F &&emit) {
        for (u32 q = 0; q <= QGLOB; ++q) {
            // the row set lives in [q, q+win]; clear exactly those words
            {
                u32 w0 = q >> 6, w1 = (q + win) >> 6;
                if (w1 >= rowbits.size()) w1 = (u32)rowbits.size() - 1;
                std::memset(&rowbits[w0], 0, (w1 - w0 + 1) * sizeof(u64));
            }
            u32 lim = (q < R) ? q : R;
            for (u32 r = 0; r <= lim; ++r) {
                if (cstate[r] == STALE) { emit(q, r, col[r].dconst); continue; }
                if (cstate[r] == UNBORN) birth(r);
                Col &c = col[r];
                u32 v;

                if (cstate[r] == SETTLED) {
                    v = eval_settled(c, q);
                } else {
                    if (q > 0 && c.prev < q) {                  // STALE branch
                        go_stale(r, q);
                        emit(q, r, c.dconst);
                        continue;
                    }
                    v = (q == 0 && r == 0) ? 1u : mex(r, q);     // f(0,0) = 1
                    ++cells;
                    if (v >= c.covbits) fatal("value past bitset", r, v);
                    bset(cov[r], v);
                    c.prev = v;
                    if (v >= q) c.lastlive = q;

                    i32 d = (i32)v - (i32)q;
                    if (d > (i32)maxd) {
                        maxd = (u32)d;
                        if ((u32)d > win - 64) fatal("d exceeded the row window", r, d);
                    }
                    u32 back = q - r;
                    for (u32 p = 1; p <= PMAX && p <= back; ++p)
                        if (c.dring[(q - p) % PMAX] != d)
                            c.lastbad[p] = (i32)(q - p) + 1;
                    c.dring[q % PMAX] = d;
                }
                rowstamp[v] = q + 1;
                if (v >= q) bset(rowbits.data(), v);
                emit(q, r, v);
                if (cstate[r] == ACTIVE && q >= c.qmax) settle(r, q);
            }
            if (q <= R) {                    // close the diagonal f(q,q)
                Col &c = col[q];
                u32 dv = (cstate[q] == STALE)   ? c.dconst
                       : (cstate[q] == SETTLED) ? eval_settled(c, q)
                                                : c.prev;
                diag[q] = dv;
                if (dv >= globbits) fatal("diagonal past global bitset", q, dv);
                bset(global.data(), dv);
            }
        }
        for (u32 r = 0; r <= R; ++r) if (cstate[r] == ACTIVE) ++unsettled;
    }

    void stats(const char *tag, double secs) const {
        std::fprintf(stderr,
            "# %s R=%u QGLOB=%u cells=%llu words/cell=%.2f low/cell=%.4f "
            "maxlow=%u ptrwords=%llu bcast=%llu maxd=%u ext=%u unsettled=%u %.2fs\n",
            tag, R, QGLOB, (unsigned long long)cells,
            cells ? (double)words / (double)cells : 0.0,
            cells ? (double)lowsteps / (double)cells : 0.0, maxlow,
            (unsigned long long)ptrwords, (unsigned long long)bcast,
            maxd, maxext, unsettled, secs);
    }
};

// ------------------------------------------------------------------- CLI ---
static void usage() {
    std::printf(
"usage: solver <mode> [options]\n"
"\n"
"  table   --rmax R [--qmax Q]     full f(q,r) grid, q=0..Q rows, r=0..R cols\n"
"                                  (entries with r>q are f(q,q))\n"
"  row     --r R [--qmax Q]        one column: `q f(q,r) d` per line\n"
"  column  --r R                   period/preperiod descriptor for that r\n"
"  census  --rmax R [--out FILE]   one descriptor line per r = 0..R\n"
"\n"
"  --alpha A     horizon qmax(r) = A*r + margin      (default 1.8)\n"
"  --margin M                                        (default 600)\n"
"  --confirm C   periodicity must hold max(C, r/4)   (default 300)\n"
"\n"
"census columns (TSV):\n"
"  r class period N dvals deathq dconst qend\n"
"    class  = live  : infinitely many P-positions, f(q,r)-q eventually periodic\n"
"             stale : finitely many; f(q,r)=dconst<q for every q>=deathq\n"
"    N      = preperiod: least q0 with f(q,r)-q exactly periodic for all q>=q0\n"
"             (for stale rows: 1 + the last q carrying a genuine P-position)\n"
"    dvals  = one period of f(q,r)-q, listed starting at q=N\n"
"    qend   = q at which the column was finalised (qend-N is the safety margin)\n");
}

static long argval(int argc, char **argv, const char *k, long d) {
    for (int i = 1; i + 1 < argc; ++i)
        if (!std::strcmp(argv[i], k)) return std::strtol(argv[i + 1], nullptr, 10);
    return d;
}
static double argvald(int argc, char **argv, const char *k, double d) {
    for (int i = 1; i + 1 < argc; ++i)
        if (!std::strcmp(argv[i], k)) return std::strtod(argv[i + 1], nullptr);
    return d;
}
static const char *argstr(int argc, char **argv, const char *k, const char *d) {
    for (int i = 1; i + 1 < argc; ++i)
        if (!std::strcmp(argv[i], k)) return argv[i + 1];
    return d;
}

static void print_col(FILE *f, const Solver &S, u32 r) {
    const Col &c = S.col[r];
    if (S.cstate[r] == STALE)
        std::fprintf(f, "%u\tstale\t0\t%u\t-\t%u\t%u\t%u\n",
                     r, c.lastlive + 1, c.deathq, c.dconst, c.qend);
    else if (S.cstate[r] == SETTLED) {
        std::fprintf(f, "%u\tlive\t%u\t%u\t", r, c.period, c.Npre);
        for (u32 j = 0; j < c.period; ++j)
            std::fprintf(f, "%s%d", j ? "," : "", c.dper[(c.Npre + j) % c.period]);
        std::fprintf(f, "\t-\t-\t%u\n", c.qend);
    } else
        std::fprintf(f, "%u\tUNSETTLED\t0\t0\t-\t-\t-\t-\n", r);
}

int main(int argc, char **argv) {
    if (argc < 2) { usage(); return 1; }
    std::string mode = argv[1];
    double alpha = argvald(argc, argv, "--alpha", 1.8);
    u32 margin   = (u32)argval(argc, argv, "--margin", 600);
    u32 confirm  = (u32)argval(argc, argv, "--confirm", 300);
    auto t0 = std::chrono::steady_clock::now();

    if (mode == "table") {
        u32 R = (u32)argval(argc, argv, "--rmax", 24);
        u32 Q = (u32)argval(argc, argv, "--qmax", R);
        Solver S; S.init(R > Q ? R : Q, alpha, margin, confirm);
        std::vector<u32> grid((size_t)(Q + 1) * (R + 1), 0);
        S.sweep([&](u32 q, u32 r, u32 v) {
            if (q <= Q && r <= R) grid[(size_t)q * (R + 1) + r] = v;
        });
        for (u32 q = 0; q <= Q; ++q)
            for (u32 r = q + 1; r <= R; ++r)
                grid[(size_t)q * (R + 1) + r] = S.diag[q];
        for (u32 q = 0; q <= Q; ++q) {
            for (u32 r = 0; r <= R; ++r)
                std::printf("%s%u", r ? " " : "", grid[(size_t)q * (R + 1) + r]);
            std::printf("\n");
        }
    } else if (mode == "row") {
        u32 r = (u32)argval(argc, argv, "--r", 0);
        u32 Q = (u32)argval(argc, argv, "--qmax", 0);
        Solver S; S.init(r, alpha, margin, confirm, Q);
        if (Q == 0) Q = S.QGLOB;
        S.sweep([&](u32 q, u32 rr, u32 v) {
            if (rr == r && q <= Q) std::printf("%u %u %d\n", q, v, (i32)v - (i32)q);
        });
    } else if (mode == "column") {
        u32 r = (u32)argval(argc, argv, "--r", 0);
        Solver S; S.init(r, alpha, margin, confirm);
        S.sweep([](u32, u32, u32) {});
        std::printf("r\tclass\tperiod\tN\tdvals\tdeathq\tdconst\tqend\n");
        print_col(stdout, S, r);
    } else if (mode == "census") {
        u32 R = (u32)argval(argc, argv, "--rmax", 1000);
        const char *out = argstr(argc, argv, "--out", nullptr);
        Solver S; S.init(R, alpha, margin, confirm);
        S.sweep([](u32, u32, u32) {});
        FILE *f = out ? std::fopen(out, "w") : stdout;
        if (!f) fatal("cannot open output file");
        std::fprintf(f, "r\tclass\tperiod\tN\tdvals\tdeathq\tdconst\tqend\n");
        for (u32 r = 0; r <= R; ++r) print_col(f, S, r);
        // Completion trailer. A census truncated by a crash, a full disk or a
        // cancelled CI job still parses as a valid (tiny) census, and every
        // number computed from it downstream would be quietly wrong. The
        // wrapper refuses any file that does not end with this line.
        std::fprintf(f, "# complete rmax=%u rows=%u\n", R, R + 1);
        if (out) { if (std::fclose(f) != 0) fatal("census write failed"); }
        S.stats("census", std::chrono::duration<double>(
            std::chrono::steady_clock::now() - t0).count());
        return 0;
    } else { usage(); return 1; }

    std::fprintf(stderr, "# %.2fs\n", std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count());
    return 0;
}
