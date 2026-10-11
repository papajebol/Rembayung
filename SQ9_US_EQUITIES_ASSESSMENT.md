# SQ9 US Equities Price-Mapping Assessment

## Scope, evidence, and conclusion in brief

This is a mathematical and architectural assessment, not a claim of trading
efficacy and not an implementation specification. No source code is present in
this repository: the only tracked project file at the time of review was an
empty `.gitkeep`. Consequently, the formulas in the request can be assessed,
but the requested inspection of the actual Python coordinate construction,
tie-breaking, bounds checks, rounding, and angular lookup cannot be performed.
No exact EP/TP/SL value that depends on those details is asserted below.

The central conclusion is that `increment = +/-1` is an affine
coordinate-to-price convention, not a topological requirement of a Square of
Nine. Replacing its magnitude by a positive scale preserves the grid and all
ordinal relationships, but changes every dollar distance. The four stated
inputs do not identify a unique scale. Any claimed unique formula must add a
normalization condition (for example, “one Daily Norm occupies *k* ordinal
steps” or “this price interval fills this part of the grid”). The value *k*, or
the selected interval and grid endpoints, is an additional assumption even if
it is hidden inside a formula.

The recommended decision is therefore conservative: keep the canonical grid
and the existing selection logic; isolate price conversion as an affine map;
do not select a new production scale until a scale convention is explicitly
approved and validated. Keeping `|increment| = 1` is a legitimate compatibility
mode, but it is not universally suitable for US equities. Unavailable levels
must produce an explicit “no signal”, never a silent fallback.

---

## Section A — Technical assessment of the described implementation

### A.1 Model stated in the request

Let an SQ9 cell have ordinal `n` in the finite domain

\[
  n\in\{1,2,\ldots,361\}.
\]

The stated map is

\[
  p(n)=S+(n-1)I,
\]

where `S` is SQ9 Start and the current implementation chooses
`I = sign(C-S)` with magnitude one. Its inverse, when `I != 0`, is

\[
  q(p)=1+\frac{p-S}{I}.
\]

`q` need not be an integer; this matters because a decimal close normally lies
between cell prices. The eligible harmonic set is described as

\[
H=\{n: r(n)=0\;\lor\;c(n)=0\;\lor\;|r(n)|=|c(n)|\}.
\]

Thus harmonic membership is a property of a cell's coordinates, not its dollar
price. For a BUY, EP candidates satisfy `p(n) < C`; for a SELL they satisfy
`p(n) > C`. TP1 minimizes distance to `C +/- DailyNorm` among whatever set the
implementation actually declares eligible, and TP2 is the next harmonic in the
profit direction.

The described stops are coordinate/ordinal operations rooted at EP1: a
181-degree stop changes to an opposite ray and applies a signed square-root
ordinal displacement of one; a 361-degree stop remains on the same ray and
applies a displacement of two. “Square-root ordinal displacement” is not
sufficient by itself to reproduce code: rounding of the transformed ordinal,
ray enumeration, orientation, center handling, and out-of-domain behavior all
matter.

### A.2 What can and cannot be verified

The following conclusions follow directly from the supplied equations:

* Price mapping is affine in ordinal space.
* Harmonic coordinates are independent of price scale.
* A finite 361-cell image has price span `360 * |I|`.
* Multiplying `|I|` multiplies all dollar separations between any two fixed
  ordinals by the same factor.

The following cannot be verified without the Python source:

* spiral orientation and the coordinate assigned to every ordinal;
* whether Start is exactly Pivot and how BUY/SELL chooses Pivot High/Low;
* the precise eligible set used for targets and ties;
* whether comparisons are strict and whether currency values are rounded;
* the actual 181/361-degree cell lookup and its failure behavior.

Accordingly, this report does not substitute the common formula
`(sqrt(price) +/- angle/180)^2` for the described implementation. That common
formula acts in price-derived square-root space. The stated system instead maps
finite grid ordinals to prices and performs ray/ordinal operations; they are not
interchangeable.

---

## Section B — The increment problem

### B.1 Essential geometry versus representation

The unit increment is **not mathematically essential** to the grid. Define a
positive magnitude `a` and direction sign `sigma`:

\[
 p_a(n)=S+\sigma a(n-1),\qquad a>0.
\]

For any two cells `i,j`,

\[
 p_a(j)-p_a(i)=\sigma a(j-i).
\]

Changing `a` is therefore an affine embedding of the same ordered ordinal set
into dollars. It does not move, add, or remove cells. Unit increment becomes
essential only if “one ordinal equals one quoted price unit” is itself declared
part of the trading methodology. That is an economic convention, not a
topological theorem.

### B.2 Invariants and non-invariants

For fixed nonzero sign and positive `a`, these are invariant:

* the 19x19 topology and 361-cell domain;
* each cell's row, column, ray, cardinal, diagonal, and harmonic status;
* ordinal order and “next harmonic” relations;
* the 181/361-degree *ordinal/coordinate* lookup rooted at a fixed EP1;
* affine ratios of distances between fixed ordinals.

These are not generally invariant:

* which cell is nearest to an externally supplied dollar Close or RawTP;
* which harmonics fall on the required side of Close;
* whether EP1/EP2/TP1/TP2 exist within the finite domain;
* which cell becomes EP1 and hence which stop lookup is initiated;
* dollar risk, dollar reward, and distances relative to Daily Norm;
* tick alignment, rounding, and executable prices.

EP ordering is preserved **conditional on the same candidate ordinals being
selected**. It is misleading to say the resulting EPs are invariant, because
changing `a` moves Close's inverse coordinate `q(C)` and may change the
candidate set.

### B.3 Why one dollar is not universal

With `a=1`, total coverage is exactly $360. More locally, if Start is Pivot and
the map points from Pivot toward Close, the number of positive ordinal steps
strictly before Close is governed by `|C-P|`, measured in dollars. A $0.30 move
and a $20 move therefore occupy about 0.30 and 20 ordinal intervals even if
they are comparable moves in instrument-relative terms. This is dimensionally
valid but cross-instrument normalization is absent.

---

## Section C — Smallest defensible candidate set

### Candidate 0: unchanged unit-dollar embedding (baseline)

**Definition.** `p(n)=S+sign(C-S)(n-1)`.

**Inputs.** Start (apparently derived from Pivot) and Close; Daily Norm remains
used for RawTP. **Assumptions.** One ordinal step means one dollar (or one unit
of the input quote). **Arbitrary parameters.** No new parameter, but the unit
choice is a pre-existing convention with no equity-wide invariance.

**Compatibility.** Exact compatibility with all existing logic. **Limits and
failures.** Sparse resolution for low-priced/narrow moves; limited $360 span;
possible missing EP2, target, or stop; scale changes under a stock split unless
all historical inputs and the convention are adjusted. **Complexity.** None.

### Candidate 1: affine normalized-price layer with an explicit scale policy

**Definition.** Work internally with

\[
 x(p)=\frac{p-S}{a},\qquad p(x)=S+a x,
\]

and let ordinal `n` correspond to signed normalized coordinate
`x = sigma(n-1)`. Here `a>0` is the price per ordinal. The grid itself is not
modified.

**Inputs.** Existing inputs plus a scale policy that determines `a` (possibly
metadata rather than manual input). **Assumptions.** Affine price differences,
not percentage/log returns, are the intended metric; the policy is stable and
defined before observing desirable output. **Arbitrary parameters.** Yes,
unless the methodology supplies an independently justified calibration
condition. The architecture is parameter-free; a concrete deployment is not.

**Compatibility.** Topology and coordinate stop algorithms are fully
compatible. Price comparisons, target nearest-neighbor selection, bounds, and
rounding must operate consistently through the conversion layer.

**Limits and failures.** A poor policy can place Close too near either boundary,
leave too few entry-side harmonics, or leave no room for TP2/stops. Very small
`a` can generate sub-tick prices; very large `a` makes levels coarse. **Complexity.**
Low conceptually: one reversible mapping boundary, validation, and display
rounding. It is still a methodology change and requires approval.

### Candidate 2: Daily-Norm unit (`a = N`), as a testable convention only

**Definition.** For positive Daily Norm `N`, set

\[
 p(n)=S+\sigma N(n-1).
\]

RawTP is then exactly one normalized unit from Close, although Close generally
does not lie on a cell.

**Inputs.** Only the existing Start, Close, direction, and Daily Norm.
**Assumptions.** One ordinal step represents one Daily Norm and Daily Norm is a
positive, consistently defined price-distance statistic appropriate for both
normalization and target construction. **Arbitrary parameters.** No numerical
constant is added, but the one-step semantic assignment is an additional
modeling assumption. `a=N/k` would add a free dimensionless `k`; nothing in the
inputs determines it.

**Compatibility.** Geometric compatibility is exact; output compatibility is
not, because candidate ordinals and EP1 can change. **Limits and failures.** A
Pivot-to-Close move smaller than one Norm provides less than one interval and
commonly too few entry candidates; large/noisy Norm makes the grid coarse;
zero or negative Norm makes the map invalid; using the same measurement to set
both scale and target mechanically fixes RawTP at one normalized unit from
Close without proving that this aligns with harmonic spacing. **Complexity.**
Low.

### Rejected as a standalone candidate: “fit the observed interval to the grid”

Formulas such as `a=|C-P|/k` or `a=(|C-P|+N)/k` look data-derived but require a
chosen ordinal span `k` and placement policy. Choosing `k=360` merely hides the
assumption that an observed endpoint belongs on a grid boundary. Mapping
`Pivot -> n=1` and `RawTP -> n=361`, for example, gives

\[
 a=\frac{|C-P|+N}{360},
\]

but deliberately consumes all profit-side range at RawTP and can make TP2
impossible when the boundary is the selected TP1. It is not recommended and is
included only to expose the hidden degree of freedom.

Tick size is externally defined rather than optimized and could be a defensible
extra datum, but one-cent steps cover only $3.60 on this grid. Percentage or log
mapping would handle price scale, but it is nonlinear in dollars and therefore
changes the stated additive RawTP and risk interpretation. Neither is a
solution using only the stated inputs.

---

## Section D — Comparative invariants and trade-offs

| Property | Unit `a=1` | Explicit affine policy | `a=N` |
|---|---:|---:|---:|
| 19x19 topology | preserved | preserved | preserved |
| Harmonic/cardinal/diagonal membership | preserved | preserved | preserved |
| Coordinate 181/361 relation for a fixed EP1 | preserved | preserved | preserved |
| Same EP/TP ordinals as legacy | yes | not guaranteed | not guaranteed |
| Total dollar span | $360 | `360a` | `360N` |
| New numeric constant | none | policy-dependent | none |
| New semantic assumption | no | yes | yes: one Norm/step |
| Cross-price normalization | none | policy-dependent | volatility-distance based |
| Unique from stated inputs | yes, by retaining convention | no | formula yes, justification no |

For fixed output ordinals `e,t,s`, reward and risk are

\[
 R=a|t-e|,\qquad L=a|e-s|,
 \qquad R/L=|t-e|/|e-s|.
\]

Thus scale cancels from reward-to-risk **only when the ordinals remain fixed**.
In the actual pipeline, Close and RawTP select ordinals, so changing scale can
change `e`, `t`, and the stop rooted at `e`; reward-to-risk is not globally
invariant. Dollar risk always scales with `a` for fixed cells.

Scaling cannot cure the finite-domain problem. It trades resolution for range:
smaller `a` gives denser dollar levels and less total coverage; larger `a` gives
more coverage and coarser levels. No affine scale can simultaneously guarantee
two entry harmonics, two profit harmonics, and both valid angular stops for
every possible Pivot, Close, Norm, and EP1 on a fixed finite grid.

---

## Section E — Numerical mapping checks and limits of verification

### E.1 Exact checks independent of spiral orientation

Assume, solely for these mapping checks, a BUY with `S = Pivot Low`, positive
`N`, and strict entry condition `p(n)<C`. These assumptions must be checked
against the missing source. Let

\[
 q_C=1+\frac{C-P}{a},\qquad
 q_T=1+\frac{C+N-P}{a}.
\]

An ordinal is on the BUY entry side exactly when `n < q_C`. RawTP is inside the
mapped price interval exactly when `q_T <= 361`. These statements identify
coverage; they do not invent harmonic results.

| Case | Pivot `P` | Close `C` | Norm `N` | Mapping | `q_C` | `q_T` | Certain result |
|---|---:|---:|---:|---|---:|---:|---|
| Low/narrow | 24.50 | 24.80 | 0.60 | `a=1` | 1.30 | 1.90 | only ordinal 1 is below Close; EP2 is impossible even if ordinal 1 is eligible |
| Low/narrow | 24.50 | 24.80 | 0.60 | `a=N` | 1.50 | 2.50 | only ordinal 1 is below Close; EP2 is impossible |
| Medium | 175.00 | 180.00 | 4.00 | `a=1` | 6.00 | 10.00 | entry ordinals 1–5; harmonic availability needs source |
| Medium | 175.00 | 180.00 | 4.00 | `a=N` | 2.25 | 3.25 | entry ordinals 1–2; harmonic availability needs source |
| High/wide | 950.00 | 970.00 | 15.00 | `a=1` | 21.00 | 36.00 | entry ordinals 1–20 and RawTP in range; exact selections need source |
| High/wide | 950.00 | 970.00 | 15.00 | `a=N` | 2.3333 | 3.3333 | entry ordinals 1–2; exact selections need source |
| Wide/overrun | 40.00 | 390.00 | 20.00 | `a=1` | 351.00 | 371.00 | RawTP lies outside the grid; TP nearest/bounds behavior needs source and TP2 may fail |
| Tiny Norm | 50.00 | 50.05 | 0.01 | `a=N` | 6.00 | 7.00 | entry ordinals 1–5; generated prices require cent/tick policy |

These examples demonstrate why price level alone does not determine suitability.
The ratio `(C-P)/a` controls entry-side ordinal capacity, while
`(C+N-P)/a` controls BUY target coverage. The analogous SELL equations reverse
the sign but have the same absolute-distance constraints.

### E.2 Why exact EP/TP/SL tables are intentionally absent

Producing EP1, EP2, TP1, TP2, SL Intraday, and SL Swing requires the exact
`n -> (r,c)` table and angular functions. Those artifacts are absent. Assigning
specific values from a conventional internet SQ9 spiral would violate the
requirement to follow the actual source and could silently reverse rays or alter
rounding. For each row above:

* EP1/EP2 can be named only after intersecting the listed entry ordinals with
  the implementation's harmonic set and applying its tie/order rules.
* TP1/TP2 require its exact eligibility, nearest tie-break, and boundary rules.
* both stops require the EP1 cell and exact ray/square-root transformation.

The precise reported failure in the first two rows is valid without those
details: fewer than two total ordinals are on the entry side, so two distinct
harmonic entries cannot exist. Other fields are “not verifiable from supplied
artifacts”, not fabricated failures or successes.

### E.3 Required verification once source is supplied

A source-faithful assessment should export or inspect, for each candidate
scale, the tuple

`(n, row, column, harmonic, price)` for all 361 cells, then trace candidate
filtering, tie-breaking, TP2 iteration, and each stop transform. Tests should
include both directions, exact-boundary and half-way ties, EP1 near every edge,
decimal prices, and out-of-range transformed stops. Expected values should be
obtained from the implementation—not a separately assumed SQ9 convention.

---

## Section F — Edge cases and unresolved assumptions

1. **Pivot equals Close.** The stated `choose_increment` returns `None`; this is
   an explicit no-signal condition unless the methodology defines another rule.
2. **Pivot extremely close to Close.** Fewer than two entry-side ordinals can
   exist. Report “insufficient eligible EP levels”; do not shrink `a` ad hoc.
3. **Norm zero, negative, missing, or non-finite.** RawTP or `a=N` is invalid.
   Validate and reject; do not substitute a default.
4. **Very small Norm.** A Norm-derived map may create sub-tick prices and false
   distinctions between levels that execute at one quote. A declared tick
   rounding policy is required, and rounding can merge or reorder outputs.
5. **Very large Norm.** RawTP can leave the finite domain under the baseline;
   with `a=N`, local harmonic resolution can be too coarse.
6. **TP1 exists but TP2 does not.** Return no TP2 (and define whether that
   invalidates the entire signal). Never wrap, extrapolate beyond ordinal 361,
   or silently reuse TP1.
7. **EP1 exists but stop lookup fails.** Return the specific angular/bounds
   failure. Never replace it with a percentage stop.
8. **Decimal precision.** Use decimal arithmetic in a future implementation;
   define input currency precision, comparison precision, display precision,
   and tick rounding separately. Floating-point artifacts must not decide ties.
9. **Very low/high prices.** Low price is not itself the issue; ordinal coverage
   ratios are. High prices can work under `a=1` if relevant dollar distances fit.
   Corporate actions expose the lack of scale invariance.
10. **Direction inconsistent with Pivot/Close.** Validate the sign and required
    entry side explicitly rather than taking an absolute value that masks the
    inconsistency.

The ten-trading-day maximum imposes no equation on this static price embedding.
It is an execution/expiry constraint unless a time-price relation is added to
the methodology. Deriving scale from ten days would invent such a relation.

The largest unresolved assumption is semantic: what physical/economic distance
is one SQ9 ordinal intended to represent? Neither geometry nor the four inputs
answers it. A second unresolved issue is operational: whether a signal requires
all six levels or permits partial output.

---

## Section G — Recommendation

1. **Do not alter the canonical 19x19 grid or angular algorithms.** They should
   remain functions of integer coordinates/ordinals.
2. **Recognize price conversion as a separate affine layer.** This is the
   mathematically clean adaptation point and preserves geometry.
3. **Do not claim a uniquely derived equity scale.** Current inputs are
   insufficient. `a=N` is the only especially simple input-only candidate, but
   “one Norm per ordinal” is an unproven semantic assumption, not a deduction.
4. **Initially retain `a=1` as a compatibility baseline and fail explicitly**
   when required levels are unavailable. This is the simplest honest system
   and permits exact parity testing with Python.
5. **Before enabling normalized mode, approve one exogenous calibration
   condition.** Examples of the *kind* of decision required are a fixed number
   of ordinal intervals per Daily Norm, a formal placement of Pivot/Close/target
   into specified ordinal regions, or an instrument metadata unit. This report
   does not choose a value, because geometry does not justify one.
6. **Evaluate practicality empirically, separately from geometry.** Measure
   level availability, tick validity, distances, and risk distributions on a
   predeclared equity sample. Predictive edge requires a separate, out-of-sample
   study and is not established here.

This recommendation may appear less convenient than an automatic scaling
formula, but it prevents an arbitrary parameter from being disguised as
mathematics. If stakeholders accept the explicit convention `a=N`, it is a
coherent normalized mode—not a uniquely correct one.

---

## Section H — Minimum future system changes (no implementation here)

Subject to approval and receipt of the Python source, the minimum architectural
change for PHP/HTML is:

1. port the original ordinal/coordinate, harmonic, EP, TP, and angular stop
   behavior exactly, including ties and failures;
2. keep integer ordinal geometry independent from price representation;
3. introduce one validated `pricePerOrdinal` value at the conversion boundary,
   defaulting to `1` for compatibility;
4. use decimal price arithmetic and a separately declared market tick/display
   policy;
5. expose mapping mode and scale provenance in every result;
6. return explicit reason codes for missing EP2, TP2, or angular stops; and
7. enforce ten-session expiry outside the geometry engine.

No indicator, AI/ML component, brokerage integration, grid enlargement, or new
trading rule is mathematically necessary.

---

## Final decisions

1. **Is `+/-1` suitable without modification?** Not universally. It is valid
   and maximally faithful, and may work for some equities, but narrow dollar
   moves can lack EPs and the finite $360 span can lack targets/stops.
2. **Most defensible alternative?** Preserve the grid and use an explicit
   affine normalized-price layer with a predeclared scale policy. There is no
   uniquely defensible numeric scale in the supplied information.
3. **Derivable from only existing inputs?** A formula such as `a=N` is
   computable, but not logically compelled. A uniquely justified scale is not
   derivable without one additional normalization assumption.
4. **Preserve 19x19 geometry?** Yes. Any positive affine scale preserves it.
5. **Preserve EP/TP/SL logic?** It preserves the algorithms and coordinate
   relationships, but not necessarily the selected ordinals or dollar outputs.
6. **Arbitrary assumptions?** The affine architecture does not; every concrete
   non-unit scale policy does unless its calibration condition is independently
   justified. `a=N` adds a semantic assumption despite adding no constant.
7. **Necessary or overengineering?** A configurable scale is unnecessary for
   exact legacy parity and should not be added merely to force signals. It is
   necessary only if measured equity cases show unacceptable no-signal rates or
   unusable distances and stakeholders adopt a principled normalization rule.
8. **Minimum PHP/HTML change?** First port the original behavior with unit scale
   and explicit failures. Architect one affine price conversion boundary so an
   approved scale policy can later replace `1` without changing SQ9 geometry.

No coding should begin until the original Python source is supplied, its exact
angular mapping is verified, and the scale convention (or baseline-only choice)
is approved.
