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
9. Bounded labels, lines, debug labels, and a latest-pattern dashboard.

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
| Minimum pole | 2.0 ATR |
| Bump acceleration multiplier | 1.8 |
| Minimum curve R² | 0.60 |
| Minimum V temporal symmetry | 0.55 |
| Minimum pattern quality | 60 |
| Candidate maximum age | 180 bars |

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
  shallow handle in the upper/lower region. With `Allow V-like cups` disabled,
  the fit must also meet the stricter 0.70 R² floor.
* `FAILED` candidates are retained internally for deterministic state transition
  and debug output, but the normal chart emphasizes forming/confirmed patterns.
* TradingView drawing limits require bounded output; older labels and lines are
  deleted. The script does not scan all historical pivot combinations.

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

1. Paste `fcpo_25_core_patterns_v1.pine` into TradingView Pine Editor.
2. Confirm that Pine Editor reports zero compiler errors before testing signals.
3. Add the indicator to an FCPO 5-minute chart.
4. Enable one pattern family at a time to isolate its geometry.
5. Start Bar Replay well before a recognizable structure and advance one candle
   at a time.
6. Inspect pivot chronology: types must alternate and no pivot may be known until
   its configured right-side bars close.
7. Inspect the stored prior trend immediately before the first pattern pivot.
8. Inspect the ATR/tick tolerance shown by debug mode across quiet and volatile
   sessions.
9. Visually extend the detected upper/lower boundary and compare it with the
   script's projected breakout line.
10. With `Require breakout close` enabled, confirm a wick crossing does not
    confirm and an actual close beyond the projected boundary plus buffer does.
11. Confirm a FORMING label appears on its knowledge bar, never on the earlier
    final-pivot bar.
12. Confirm CONFIRMED or FAILED resolution removes the orange forming state.
13. Replay the same interval twice and verify identical IDs and no repeated
    same-structure labels.
14. Record false positives separately for each family, then tune pivot and ATR
    settings rather than adding fixed price or percentage constants.

Review geometry first, followed by prior trend, classification, breakout
accuracy, duplicate frequency, and false positives. Do not interpret detections
as entries, exits, or evidence of profitability.
