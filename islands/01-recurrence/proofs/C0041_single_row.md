# C0041 -- single-row run lemma (proved)

**Claim.** Fix a row `c` and a value `p*`. Let `S(c, p*) = { q : f(q,c) = p* }`
(valid occurrences, so `p* >= q`). If `q` and `q + t - 1` both lie in
`S(c, p*)` with every intermediate column too (a run of length `t`), and
`q >= N(c)` (the witness row is in its periodic regime at the run's start),
then `t <= p_c`, the period of row `c` (with `p_c := 1` for stale rows, whose
`S` is empty in this regime anyway).

**Proof.** Write `B_c(a) = f(c+a, c) - (c+a)` and `a0 = q - c`. The run says
`B_c(a0 + j) = p* - q - j =: h - j` for `j = 0, ..., t-1` (a unit descent).
`a0 = q - c >= N(c) - c = u_c`, so `B_c` is `p_c`-periodic at `a0`:
`B_c(a0) = B_c(a0 + p_c)`. But the descent chain gives
`B_c(a0 + p_c) = h - p_c` whenever `p_c <= t - 1`, and `h - p_c != h`.
Hence `t - 1 < p_c`, i.e. `t <= p_c`. For a stale row `B_c` is undefined for
`a >= u_c`, so `S(c, p*)` is empty in the regime `q >= N(c)` and the statement
holds vacuously. QED.

**Consequence for C0039.** In a POST-ONSET plug run for row `r` (columns
`q >= max_{c<r} N(c)`), every witness `c < r` satisfies `q >= N(c)`, so each
individual witness row covers at most `p_c <= 9` consecutive columns of the
run (periods to r=50000 are <= 9). The runs of length 459 (C0040) survive only
because their columns sit PRE-onset for their witness rows (e.g. run p*=1106
starts at q=648 while its witness row 647 has N(647) ~ 915 -- the run feeds on
TRANSIENT values of the witness rows). Therefore the whole of C0039 reduces to
the INTERLEAVE question: can level sets of DIFFERENT rows (each a union of
<= p_c-consecutive pieces, scattered by the within-period wiggle of
`g_c(q) = q + B_c(q-c)`) jointly cover more than c0 consecutive columns
post-onset? Observed: no (c0 = 6). This is now a statement purely about the
periodic tails `B_c`, which are finite computable objects.
