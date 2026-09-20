# Where Byrnes loses effectivity

**Sources read in full.**

- S. Byrnes, *Poset-Game Periodicity*, Intel Science Talent Search version,
  20 pp., from `http://e.math.hr/dvijeigre/byrnes/main.pdf`. Published as
  INTEGERS **3** (2003), #G03. The Siemens version is the same proof.
- D. Zeilberger, *Chomp, Recurrences and Chaos(?)*, 2003 -- the **TeX source**
  `.../mamarim/mamarimTeX/byrnes.tex`, not the PDF (see the warning below).

Neither is committed: this repo is public. Run
`python -m GROUND_TRUTH.fetch_sources` to pull both into `GROUND_TRUTH/data/`.

> **Fetch warning for later sessions.** The PDF that MISSION.md points at,
> `https://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimPDF/byrnes.pdf`, is
> **truncated**: it is 6 pages and stops in the middle of the 2-rowed warm-up,
> before the Ultimate-Periodicity Theorem. Everything quoted below from
> Zeilberger comes from the **TeX source**,
> `.../mamarim/mamarimTeX/byrnes.tex`, which is complete (1030 lines). Do not
> re-read the PDF and conclude the exposition is unfinished.
> Also: `https://math.colgate.edu/~integers/g3/g3.pdf` is **not** Byrnes; it
> serves Hegarty-Larsson, INTEGERS 6 (2006) #A03.

---

## The short answer

There are two proofs and they fail differently, which matters a great deal for
how the budget should be spent.

**Byrnes' general poset-game proof loses effectivity in exactly one place: the
converse direction of Lemma 4**, which produces two integers `M` and `N` out of
the bare *finiteness* of a set, with no bound on either. That one step is the
sole source of the non-computable quantity `W(A,k)`, and `W(A,k)` is the **only**
non-computable term in the final bound. The famous pigeonhole (Lemma 9) is
**not** the problem — it is fully explicit.

**Zeilberger's 3-row specialisation does not lose effectivity at all.** Its
pigeonhole is over an explicitly counted state space. What it needs instead are
two quantities that the induction supplies but does not bound a priori: a bound
on the values of `p-q`, and a bound on the lcm of the periods below `r`.

So the sharp question for this project is not "where is the non-effective step"
in the singular. It is:

> **(Z1)** Give an explicit `C` with `f(q,r) - q <= C r` for all `q >= r >= 1`.
> **(Z2)** Give an explicit bound on `lcm{period(c) : c < r}`.
>
> These two together already yield an explicit (astronomical) bound on `N(r)`
> through Zeilberger's argument, with nothing else added. **(Z1) is already
> proved at `q = r`** by Byrnes' own Lemma 5 (section 3 below); only the
> large-`q` half is missing.

and, on the Byrnes route,

> **(B1)** Give an explicit `K(r)` bounding the last `q` at which a *stale* row
> `r` carries a P-position.
>
> This is exactly `W(A,0)`, and it is the only thing Byrnes' proof leaves
> uncomputable.

`GROUND_TRUTH/seed_check.md` measures both quantities:
`lastlive(r) = sqrt(2) r + O(1)` (deviation in `[-0.12, +3.50]` over 29289
stale rows to `r = 50000`) and `max_q (f(q,r) - q) = (sqrt(2)/2) r + O(1)`.

---

## 1. Byrnes: the step, quoted

### 1.1 The definitions the step feeds

`A_{m,n}` is the position obtained from `A u C u D` (a finite set `A` and two
infinite chains `C`, `D`) by the two moves `c_{m+1}` and `d_{n+1}`, and

> `Q(A) = {k in N_0 | only finitely many positions of the form A_{m,n} have g-value k}`

For 3-row Chomp with the third row fixed and `k = 0`, this reads: **`0 in Q(A)`
iff the row has only finitely many P-positions**, i.e. iff the row is what the
solver calls `stale`. `0 not in Q(A)` iff the row is `live`. Keep that
identification in mind; everything below turns on it.

### 1.2 The step (Lemma 4, converse direction, p. 8)

> **Lemma 4.** `k in Q(A)` if and only if one of the following is true: (i)
> There exists `m, n in N_0` such that `c_{m+1} > d_{n+1}` and `g(A_{m,n}) = k`,
> or (ii) there exists an `a in A`, `m, n in N_0` with `a < c_{m+1}`,
> `a < d_{n+1}`, and `g(A_{m,n} - {x in X | x >= a}) = k`.
>
> *Proof.* [...] **Finally, suppose that `k in Q(A)`. Since any `A_{m,n}` is
> finite, we can find an `M` and `N` such that, if `c_M in A_{m,n}` or if
> `d_N in A_{m,n}`, then `g(A_{m,n}) != k`.** By Lemma 2, we can find a `y > N`
> such that `g(A_{M,y}) > k`. Let `z` be a move that takes `A_{M,y}` to a
> position with g-value `k`. [...]

**That bolded sentence is the whole problem.** The reasoning is: `k in Q(A)`
says the set of positions with g-value `k` is finite; each such position is a
finite subset of `X`; so their union is finite; so some `c_M` and some `d_N`
lie outside all of them. Perfectly correct, and perfectly useless
computationally — *"this set is finite"* is exactly the hypothesis that carries
no bound. To compute `M` and `N` you would have to already possess the complete
list of positions with g-value `k`, which is what you are trying to determine.

Note the asymmetry, which is the good news: the two **forward** directions of
Lemma 4 are effective and even quantitative. Direction (i) gives "at most `m+1`
different positions of the form `A_{x,y}` with g-value `k`"; direction (ii)
gives "at most `m+n+2`". Only the converse is non-constructive.

### 1.3 How the damage propagates: `T(A,k)` and `W(A,k)` (p. 8)

Immediately after that proof:

> If `k in Q(A)`, whether (i) or (ii) occurs, there is a number
> `T(A,k) in N_0` such that, if `n >= T(A,k)`, then there is a move from
> `A_{m,n}` to a position with g-value `k`, no matter what the value of `m`. If
> (i) holds, then `c_{m'+1} > d_{n'+1}` with `g(A_{m',n'}) = k`, and if (ii)
> holds, then, for some `a in A`, `a < c_{m'+1}`, `a < d_{n'+1}`, and
> `g(A_{m',n'} - {x in X | x >= a}) = k`. For each `m`, by Lemma 2, there exists
> an `n_m` such that, if `n >= n_m`, then `g(A_{m,n}) > k`. If we let
> `T(A,k) = max(n_0, n_1, ..., n_{m'}, n'+1)`, it will have the desired
> property. Now, let
>
> `W(A,k) = max({T(B,j) | B subset A, j <= k, j in Q(B)})`
>
> with `max(empty)` interpreted as 0. We will use this function later.

The `(m', n')` here **are** the witnesses that Lemma 4's converse produced from
`M` and `N`. So `T(A,k)` inherits the unboundedness, and `W(A,k)` with it.

Two things worth noticing, because they narrow the target:

1. **The `n_m` are effective, contrary to how the passage reads.** Byrnes cites
   Lemma 2 (distinctness of `g(A_{m,n})` over `n`), which alone gives no bound.
   But **Lemma 5** — *"If `g(A_{m,n}) = k`, then `n - m <= |A| + k`"* — is
   unconditional, so `n_m <= m + |A| + k + 1` outright. Hence
   `T(A,k) <= max(m' + |A| + k + 1, n' + 1)`.
2. Therefore **the entire non-effectivity of the paper reduces to bounding the
   least Lemma-4 witness `(m', n')`.** One pair of integers.

### 1.4 The pigeonhole is *not* where effectivity dies (Lemma 9, p. 14)

This is worth stating loudly because the obvious guess — "the pigeonhole" — is
wrong, and a session that goes looking there will waste itself.

> Let `p = lcm({p_{B,j} | B in H, j <= k, j not in Q(B)} u {p_{A,j} | j < k, j not in Q(A)})`
> with `lcm(empty)` interpreted as 1, and let
>
> `N = max({N_{B,j} | ...} u {N_{A,j} | ...}) + |A| + k + max(|A| + k, W(A,k))`
>
> [...] `S(m) subset {-|A|-k, ..., |A|+k-1}`. This means that there are at most
> `2^{2|A|+2k} = 4^{|A|+k}` possibilities for `S(m)`. Let `m_p` be the smallest
> nonnegative residue of `m (mod p)`. There are clearly `p` possibilities for
> `m_p`, so there are at most `4^{|A|+k} p` possible pairs `(S(m), m_p)`. **By
> the pigeonhole principle, there are two different numbers `m_1, m_2` with
> `N <= m_1 < m_2 <= N + 4^{|A|+k} p`** such that `S(m_1) = S(m_2)` and
> `(m_1)_p = (m_2)_p`.
>
> [...] Letting `N_{A,k} = m_1` and `p_{A,k} = m_2 - m_1`, we get [periodicity].

The pigeonhole is over a **counted** space, and it hands back explicit
inequalities:

```
    p_{A,k}  <=  4^{|A|+k} * p
    N_{A,k}  <=  max(sub-N's) + |A| + k + max(|A|+k, W(A,k)) + 4^{|A|+k} * p
```

Every symbol on the right is computable from `(A, k)` and the induction —
**except `W(A,k)`**. That is the whole audit of Byrnes in one line:

> **Give an explicit bound on `W(A,k)` and Byrnes' theorem becomes effective,
> with no other change to the proof.**

### 1.5 Where the unbounded search surfaces (Lemma 10 / Corollary 1, p. 17)

The consequence, stated by Byrnes himself without disguise:

> *Proof.* [...] **If we systematically try the countable number of possible
> solutions to `f_{A,k}` (of types (I), (II), and (III)), we will eventually
> find one that works, in a finite amount of time.**

and then

> **Corollary 1.** [...] we can calculate `f_{A,k}(m)` [...] in `O(log m)` time.
>
> *Proof.* By Lemma 10, **after some finite amount of time independent of `m`**,
> we can solve `f_{A,k}`. [...]

This is a genuine "terminates, with no computable bound on when". It is a
*symptom* of 1.2, not an independent gap: guess-and-verify is precisely what one
resorts to when the witness bound is missing.

### 1.6 Deciding `Q` is the same problem

Lemma 9's recursion also has to know, for each sub-pair `(B, j)`, whether
`j in Q(B)`. There is no a priori bound on how far to look before declaring a
row live. In our language: *how long must I watch a row before I may conclude it
will never die?* That is the same quantity as `T`, approached from the other
side. Both routes bottom out at one question.

---

## 2. Zeilberger: a different proof with a different weak point

Zeilberger's exposition is not a retelling of Byrnes. It re-proves the 3-row
case through a finite-state argument, and — this is the part that changes what
this project should do — **his pigeonhole is explicit.**

His frame: `[c,a,b]` with `c` columns of height 3, `a` of height 2, `b` of
height 1, so `a = q - r` and **`b = p - q`**. `B_C(a)` is the unique `b` making
`[C,a,b]` a loser; `I_a = W_C(a)` is the set of "instant winners", built from the
solved rows `c < C`.

> **Fundamental Recurrence.**
> `L_a = mex(I_a u {L_{a-1}-1, L_{a-2}-2, ..., L_0 - a})`
>
> **Lemma Bounded:** If the sets `I_a` are (uniformly) bounded, and `M-1` is an
> upper bound, (i.e. `max(I_a) <= M-1` for all `a > 0`) then `L_a <= M`, for all
> `a > 0`.
>
> **Ultimate-Periodicity Theorem:** If `I_a` is ultimately-periodic then the
> sequence `L_a` either terminates (with the last value being 0), or else is
> ultimately-periodic.
>
> *Proof:* Since `I_a` is ultimately-periodic the set of finite sets
> `{I_a ; a > 0}` is finite, and hence bounded. Let `M-1` be the (least) upper
> bound. By Lemma Bounded, `L_a <= M`. [...] the hitherto "infinite memory"
> recurrence becomes a "finite memory" recurrence [...]
>
> `L_a = mex(I_a u {L_{a-1}-1, L_{a-2}-2, ..., L_{a-M}-M})`
>
> Introducing the 'states' `S_a := (I_a ; L_{a-1}, L_{a-2}, ..., L_{a-M})` [...]
> **Since `L_a` is bounded, and `I_a` is ultimately-periodic, it follows that
> there are only finitely many states. By the venerable Pigeon-Hole Principle,
> sooner or later we must visit a previously-visited 'state'** [...]

Count the states. There are at most `p_r` distinct `I_a` in the tail and each of
the `M` remembered `L` values lies in `[0, M]`, so

```
    N(r) + period(r)   <=   p_r * (M_r + 1)^{M_r}
```

with

```
    M_r  =  1 + max over c < r, over a, of  B_c(a)
         =  1 + max over c < r of  max_q ( f(q,c) - q )
    p_r  =  lcm{ period(c) : c < r }.
```

Zeilberger says so in as many words:

> How to turn this into an algorithm? **The 'theoretical' upper bound for the
> period is enormous, but is hardly (and perhaps never) achieved.**

He is right that it is enormous; the point for us is that **it exists and is
explicit.** Nothing in his argument appeals to unbounded finiteness. The
pigeonhole is over `p_r (M_r+1)^{M_r}` states, counted.

So on this route the missing ingredients are not non-constructive steps at all.
They are two *a priori* bounds that the induction currently only produces a
posteriori:

- **(Z1)** an explicit bound on `M_r`, i.e. on `max_q (f(q,c) - q)` for `c < r`;
- **(Z2)** an explicit bound on `lcm{period(c) : c < r}`.

`M_r` is, up to 1, the largest `p - q` that occurs anywhere in rows below `r`.
(Note this is *not* the same as the largest diagonal entry. Brouwer proves that
`f(q,q)` is the largest element of column `q` — `r` varying, `q` fixed — which
bounds `f(q,c) - q <= f(q,q) - q`, and that right-hand side grows with `q`. The
solver confirms the two differ: `max_q (f(q,c)-q)` exceeds `f(c,c)-c` for 221 of
the 2001 columns `c <= 2000`, though never by more than **2**.)

Measured: `max_q (f(q,r) - q) / r` is at most **2**, attained at `r = 1`, and
tends to `1/sqrt(2) = 0.7071` (it is `0.70800` at `r = 2000`). So `C = 2` is
true with margin, and the real content of (Z1) is only that the maximum over `q`
is not attained far out — see section 3.

(Z2) is MISSION.md section 4's stated *secondary* target. Observed periods to
`r = 50000` are `{1,2,3,4,6,8,9}`, whose lcm is 72.

---

## 3. What has to be made quantitative, precisely

Three statements, in increasing order of difficulty. Each is stated so that
proving it is a self-contained job.

**(B1) — the Byrnes gap, stated for 3-row Chomp.**
> Exhibit a computable `K` such that for every `r` whose row is stale (only
> finitely many P-positions `(p,q,r)`), every such P-position has `q <= K(r)`.

This is `W(A,0)` and it is the *only* thing Byrnes' proof does not supply.
Equivalently, in Lemma 4's terms: bound the least witness `(m', n')`.
Measured: `K(r) = sqrt(2) r + 4` suffices for all `r <= 50000`
(`GROUND_TRUTH/seed_check.md`, section 5). Anything computable will do — `3r`,
`r^2`, `2^r`.

**(Z1) — the Zeilberger gap, and it is half done already.**
> Exhibit an explicit `C` with `f(q,r) - q <= C r` for all `q >= r >= 1`.

**Byrnes' Lemma 5 already gives the `q = r` case, unconditionally.** In his
notation, *"If `g(A_{m,n}) = k`, then `n - m <= |A| + k`"*, and the 3-row
reduction with the third row fixed at `r` has `k = 0`, `m = q - r`, `n = p - q`,
and `A` = the `3r` cells of the `r` height-3 columns minus the poison, so
`|A| = 3r - 1`. Lemma 5 therefore reads

```
    (p - q) - (q - r)  <=  3r - 1        for every P-position (p,q,r)
```

The solver confirms this over every P-position with `q, r <= 2000`, and it is
**tight**: equality holds at `(p,q,r) = (3,1,1)`, and nowhere is it violated.
Setting `q = r` gives the diagonal bound

```
    f(r,r)  <=  4r - 1                   (proved, explicit)
```

again tight at `r = 1` (`f(1,1) = 3`). Measured, `f(q,q)/q` has maximum 3 (at
`q=1`), is at most 2 for `q >= 2`, and tends to `1 + sqrt(2)/2 = 1.70711`; and
`f(q,q) - (1+sqrt(2)/2) q` lies in `[-1.153, +2.050]` for `q <= 2000`, against
Brouwer's reported `[-1.310, +2.141]` below `n = 130000`.

What is **missing** is only that `n <= m + |A|` degrades as `m` grows: it bounds
`f(q,r) - q` by `(q - r) + 3r - 1`, which is `O(r)` at `q = r` but `O(q)` for
large `q`. So the residual content of (Z1) is exactly:

> Show that `max_q (f(q,r) - q)` is attained at, or within `O(1)` of, `q = r` —
> or bound it any other way.

The data says the excess over `f(r,r) - r` is **never more than 2** for
`r <= 2000`. This is a small, sharply posed, checkable statement, and it is the
cheapest real theorem visible anywhere in this problem.

**(Z2) — the period gap.**
> Exhibit an explicit bound on `lcm{period(c) : c < r}`.

Open (MISSION.md section 4, secondary target). Note that a bound on the
*periods* is more than is needed: a bound on their lcm suffices, and lcm-bounds
are sometimes easier.

**Given (Z1) and (Z2), Zeilberger's argument yields, with no further input:**

```
    N(r)  <=  lcm{period(c) : c<r}  *  (C r + 2)^{C r + 1}
```

an explicit computable bound of the form `r^{O(r)}`. MISSION.md section 4 says
*"A bound of any computable form (`C r log r`, `C r^2`, anything effective) is a
success."* By that standard this route is a success once (Z1) and (Z2) are in
hand, and (Z1) alone looks tractable.

---

## 4. The gap between the proof and the truth

| quantity | what the proofs give | what the solver measures |
|---|---|---|
| `N(r)` via Byrnes | `max(sub-N) + |A| + k + max(..., W) + 4^{|A|+k} p`, `W` uncomputable | `sqrt(2) r + O(1)`, `|error| < 5.70` for `r <= 50000` |
| `N(r)` via Zeilberger | `p_r (M_r+1)^{M_r}`, i.e. `r^{Theta(r)}` | same |
| `W(A,0)` / `K(r)` | uncomputable | `sqrt(2) r + O(1)`, error in `[-0.12, +3.50]` |
| `M_r` (max `p-q`) | `<= (q-r) + 3r-1` (Lemma 5); `O(r)` only at `q=r` | `(sqrt(2)/2) r + O(1)`, ratio `<= 2` |
| `f(r,r)` | `<= 4r - 1` (Lemma 5, tight at `r=1`) | `(1+sqrt(2)/2) r + O(1)` |
| period | `4^{|A|+k} p` | `{1,2,3,4,6,8,9}`, lcm 72, to `r = 50000` |

The distance from `r^{Theta(r)}` to `sqrt(2) r` is the real content of the
problem. MISSION.md section 5 is explicit that closing it is *not* the priority
— *"Effectivity beats sharpness"* — and this audit says the effectivity half is
closer than the mission statement assumes.

---

## 5. Consequences for how the two islands should open

**Island 01 (recurrence-internal).** The localisation is done; do not redo it.
Open on the residual half of **(Z1)**: Byrnes' Lemma 5 already gives
`f(q,r) - q <= (q-r) + 3r - 1`, so all that is needed is that the maximum of
`f(q,r) - q` over `q` is not attained far from `q = r` (observed excess over
`f(r,r) - r` is at most 2 for `r <= 2000`). Brouwer's two proved lemmas — the
diagonal is the maximum of its column, and there are at least `p/3` P-positions
`(q,q,r)` with `q <= p` — are the natural starting materials. If that lands,
write out the Zeilberger chain to get an explicit `N(r) <= r^{O(r)}` conditional
only on (Z2), and log it. Then attack **(B1)** — a bound on how far a stale row
can run — which is the single quantity Byrnes leaves open and is the more
interesting of the two.

**Island 02 (renormalisation).** The `sqrt(2)` is not a fact about the
non-trivially-periodic rows; it is a fact about *all* rows, and for stale rows
it is *equivalent*, by an exact identity, to strip bounds on A029901 and A029902
about the Friedman-Landsberg lines `b n` and `a n` with `b = sqrt(2) a`
(`GROUND_TRUTH/seed_check.md`, section 5). So the renormalisation target is not
"explain `sqrt(2)`" — it is: **prove a strip bound `|A029902(n) - a n| <= K` for
an explicit `K`.** That single bound delivers (B1), hence effective Byrnes, and
it is exactly the kind of statement the renormalisation picture is supposed to
produce. Brouwer's own measured strips (`[-1.853, +0.940]` and
`[-1.506, +1.493]` below `n = 130000`) are the target's numerical shape.

**Do not**, on either island, attack the pigeonhole in Byrnes' Lemma 9 or in
Zeilberger's Ultimate-Periodicity Theorem. Both are already explicit. That is
the trap this audit exists to close off.
