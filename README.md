# FCPO 25 Core Chart Pattern Detector V1

This repository contains a TradingView Pine Script v6 indicator that detects the
25 requested classical chart-pattern families from confirmed swing pivots. The
implementation is deliberately an **indicator**, not a trading strategy, and
does not claim or imply profitability.

## Architecture

`fcpo_25_core_patterns_v1.pine` follows a bounded event pipeline:

1. ATR and tick-size normalization.
2. Confirmed `ta.pivothigh` / `ta.pivotlow` events normalized into a capped,
   strictly alternating swing array. A same-type pivot replaces the previous
   swing only when it is more extreme. Simultaneous high/low pivots are resolved
   by the larger ATR-normalized excursion from the last structural pivot.
3. A per-bar, precomputed trend model combining pre-pattern market structure,
   normalized regression slope, and EMA alignment/slope.
4. Geometry detectors evaluated only when a new pivot is confirmed.
5. Pattern-specific geometry scoring and a shared trend/quality gate.
6. Typed candidate objects store both upper and lower boundary anchors. Active
   candidates project those exact boundaries on each confirmed bar for
   close/wick breakout or geometry-aware invalidation.
7. Contextual reversal/continuation classification after breakout.
8. Signature, overlap, start proximity, and boundary-similarity based same-type
   duplicate suppression. A superior duplicate replaces the complete object.
9. Confirmed same-family candidates pass through a second display cluster using
   direction, prior context, overlap, breakout proximity, and boundaries. Raw
   candidate state remains available for debugging.
10. Owned, bounded drawings follow `Latest Only`, `Last N`, or `All` mode, with
   `Latest Only` as the default, plus managed labels and a compact dashboard.

Trend history is read at `patternStartBar - 1`, never at the breakout bar.
Because a pivot becomes available only after its right bars have elapsed, the
script never backdates a state label to a point where the pattern was
unknowable. Forming labels are placed on the knowledge bar and deleted when the
candidate confirms or fails. Geometry lines may still connect historical pivots.

## Implemented core families

1. Double Top
2. Double Bottom
3. Triple Top
4. Triple Bottom
5. Head and Shoulders
6. Inverse Head and Shoulders
7. Rounding Top
8. Rounding Bottom
9. Diamond Top
10. Diamond Bottom
11. V-Top
12. V-Bottom
13. Megaphone / Broadening
14. Bump and Run Top
15. Bump and Run Bottom
16. Rising Wedge
17. Falling Wedge
18. Ascending Triangle
19. Descending Triangle
20. Symmetrical Triangle
21. Bullish / Bearish Flag
22. Bullish / Bearish Pennant
23. Rectangle
24. Cup and Handle / Inverted Cup and Handle
25. Continuation Diamond

Directional variants share one family detector where the specification treats
them as one core family.

## Defaults

| Setting | Default |
|---|---:|
| Pivot left / right bars | 3 / 3 |
| Maximum stored pivots | 40 |
| ATR length | 14 |
| ATR tolerance multiplier / cap | 0.20 / 0.40 |
| Minimum tolerance ticks | 2 |
| Breakout ATR multiplier | 0.05 |
| Fast / slow EMA | 20 / 50 |
| Pre-pattern trend window | 30 |
| Normalized trend slope threshold | 0.035 ATR/bar |
| Up/down trend score threshold | +3 / -3 |
| Minimum trend strength | 55 |
| Minimum prior-trend persistence | 10 bars |
| Minimum pole | 2.0 ATR |
| Bump acceleration multiplier | 1.8 |
| Minimum curve R² | 0.60 |
| Minimum V temporal symmetry | 0.55 |
| Minimum pattern quality | 60 |
| Candidate maximum age | 180 bars |
| Wedge bars / start width / contraction | 8 / 1.0 ATR / 0.20 |
| Maximum wedge apex distance | 3× pattern duration |
| Triangle bars / start width / contraction | 8 / 1.0 ATR / 0.20 |
| Rectangle bars / height | 8 / 0.75 ATR |
| Double/triple minimum depth | 0.75 ATR |
| Minimum V leg | 1.0 ATR |
| Minimum rounding height/depth | 1.0 ATR |
| Drawing Mode / Last N | Latest Only / 5 |

## Deliberate V1 approximations and limitations

* Pivot geometry is a deterministic abstraction of hand-drawn patterns. Complex
  families use recent alternating extrema and normalized boundary lines, so
  visual judgment can differ from the detector.
* Rounding and cup bodies use quadratic least-squares curvature and R² over the
  pattern interval. Handles are measured from confirmed pivots in the upper (or
  lower) portion; V-like cups are rejected unless explicitly enabled.
* Diamond detection compares an early width, maximum width, and contracted late
  width. Breakouts use projected upper/lower contracting sides. Reversal and
  continuation subtypes are explicitly gated by prior trend and direction.
* Bump-and-run uses chronological least-squares regressions over bounded lead-in
  and bump segments. The bump must accelerate by the configured multiplier and
  the run must cross the projected lead-in reference. It does not attempt
  log-chart trendlines.
* V patterns require opposite normalized legs and a strong prior trend. Their
  minimum leg length and symmetry are pivot-based rather than tick-path based.
* Flags require approximately parallel countertrend boundaries; pennants require
  convergence. Both require an ATR-normalized pole ending exactly where the
  consolidation starts. Consolidation range ends at the final pattern pivot,
  excluding the right-side pivot-confirmation bars.
* Cup variants require ATR-similar rims, quadratic fit, meaningful depth, and a
  shallow handle in the upper/lower region. The left rim and right rim are the
  first and third pivots; the fourth confirmed pivot completes the handle, so a
  candidate does not wait for a breakout-high pivot. With `Allow V-like cups`
  disabled, the fit must also meet the stricter 0.70 R² floor.
* Wedges must meet minimum duration, ATR-normalized starting width, contraction,
  mirrored slope inequalities, and a stable future apex no farther than the
  configured duration multiple. Wedges also require a persistent, non-sideways
  prior trend.
* Rounding structures require a central quadratic vertex, opposite left/right
  segment slopes, minimum R², and meaningful ATR-normalized height/depth.
* `FAILED` candidates are retained internally for deterministic state transition
  and debug output, but the normal chart emphasizes forming/confirmed patterns.
* TradingView drawing limits require bounded output; older labels and lines are
  deleted. The script does not scan all historical pivot combinations.

## Heuristic scores and display clustering

`Quality` is a **comparative heuristic**, not statistical confidence. Geometry
starts at zero and earns pattern-specific points from valid proportions such as
duration, width, contraction, symmetry, curvature, pole strength, or boundary
accuracy. A confirmed result combines:

* Geometry: 50%
* Prior context: 20%
* ATR-normalized breakout strength: 30%

Trend strength also starts at zero: market structure contributes 35 points,
normalized slope 25, EMA direction/slope alignment 15, and persistent trend
duration 25. Reversal and continuation candidates must meet both configured
strength and persistence gates. Strong trend cannot make structurally invalid
geometry valid, and `Show low-quality patterns` bypasses only the numeric quality
threshold.

Confirmed display clustering suppresses only same-code, same-direction patterns
with matching prior context, substantial time overlap, nearby breakout bars, and
similar projected boundaries. Different families remain independently visible.
Drawing ownership allows obsolete pattern lines to be removed without deleting
the detector's raw candidate lifecycle.

## Static checks

Run:

```bash
python3 tests/test_pine_static.py
git diff --check
```

The repository test checks known source-level invariants, including Pine v6
indicator mode, all 25 family identifiers, explicit `na` typing, alternating
pivot replacement, dynamic boundaries, honest forming-label placement, and
single-object candidate storage. **It is not a Pine compiler and does not
substitute for compiling in TradingView Pine Editor.**

## TradingView compiler and Bar Replay validation

### Phase 1 — Compile

Paste `fcpo_25_core_patterns_v1.pine` into Pine Editor and require zero compiler
errors before evaluating any detection.

### Phase 2 — Isolate families

Add the indicator to FCPO M5 and enable one pattern family at a time. Keep the
initial defaults until that family's geometry has been inspected.

### Phase 3 — Bar Replay

Begin before a recognizable structure and advance one bar at a time. Pivots must
alternate, appear only after right-side confirmation, and FORMING labels must
appear on the knowledge bar rather than the historical pivot.

### Phase 4 — Verify geometry

Check ATR width/depth, touch count, duration, slopes, contraction/expansion,
rounding vertex, wedge apex, pole segmentation, and pattern-specific proportions.
Use debug output to record the principal rejection reason and earned scores.

### Phase 5 — Verify prior trend

Confirm that trend state, strength, and persistence come from immediately before
the first pattern pivot. A weak sideways context must not become a wedge reversal
or continuation.

### Phase 6 — Verify breakout boundary

Compare the projected pattern boundary with price. With close confirmation on, a
wick is insufficient. With it off, a candle piercing both bilateral boundaries
must remain unconfirmed until an unambiguous later breakout.

### Phase 7 — Verify duplicate/display suppression

Replay the interval twice, check deterministic IDs, and verify same-family
structural variants cluster while different valid families coexist. Test all
three drawing modes; `Latest Only` must remove the prior pattern's owned lines.

### Phase 8 — Statistics only after correctness

Only after geometry, context, boundary, timing, and clustering are manually
accepted should pattern occurrence/outcome statistics be collected. Do **not**
collect profitability statistics or treat detections as trade entries at this
stage.

Review geometry first, followed by prior trend, classification, breakout
accuracy, duplicate frequency, and false positives. Do not interpret detections
as entries, exits, or evidence of profitability.
