# FCPO 25 Core Chart Pattern Detector V1

This repository contains a TradingView Pine Script v6 indicator that detects the
25 requested classical chart-pattern families from confirmed swing pivots. The
implementation is deliberately an **indicator**, not a trading strategy, and
does not claim or imply profitability.

## Architecture

`fcpo_25_core_patterns_v1.pine` follows a bounded event pipeline:

1. ATR and tick-size normalization.
2. Confirmed `ta.pivothigh` / `ta.pivotlow` events stored in capped arrays.
3. A per-bar, precomputed trend model combining pre-pattern market structure,
   normalized regression slope, and EMA alignment/slope.
4. Geometry detectors evaluated only when a new pivot is confirmed.
5. Pattern-specific geometry scoring and a shared trend/quality gate.
6. Active candidates updated on confirmed bars for close/wick breakout or
   invalidation.
7. Contextual reversal/continuation classification after breakout.
8. Signature/overlap-based same-type duplicate suppression.
9. Bounded labels, lines, debug labels, and a latest-pattern dashboard.

Trend history is read at `patternStartBar - 1`, never at the breakout bar.
Because a pivot becomes available only after its right bars have elapsed, the
script never backdates a label to a point where the pattern was unknowable.

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
| Minimum curve R² | 0.60 |
| Minimum pattern quality | 60 |
| Candidate maximum age | 180 bars |

## Deliberate V1 approximations and limitations

* Pivot geometry is a deterministic abstraction of hand-drawn patterns. Complex
  families use recent alternating extrema and normalized boundary regression,
  so visual judgment can differ from the detector.
* Rounding and cup bodies use quadratic least-squares curvature and R² over the
  pattern interval. Handles are measured from confirmed pivots in the upper (or
  lower) portion; V-like cups are rejected unless explicitly enabled.
* Diamond detection splits the pivot sequence at its midpoint and compares range
  expansion then contraction. Top/bottom versus continuation is resolved from
  stored prior trend and confirmed breakout direction.
* Bump-and-run uses an ATR-normalized lead-in slope followed by an accelerated
  excursion and trendline break; it does not attempt log-chart trendlines.
* V patterns require opposite normalized legs and a strong prior trend. Their
  minimum leg length and symmetry are pivot-based rather than tick-path based.
* Flags require approximately parallel countertrend boundaries; pennants require
  convergence. Both require an ATR-normalized pole and a consolidation no larger
  than a configurable fraction of that pole.
* `FAILED` candidates are retained internally for deterministic state transition
  and debug output, but the normal chart emphasizes forming/confirmed patterns.
* TradingView drawing limits require bounded output; older labels and lines are
  deleted. The script does not scan all historical pivot combinations.

## TradingView Bar Replay test procedure

1. Open Pine Editor, paste `fcpo_25_core_patterns_v1.pine`, save, and add it to
   an FCPO 5-minute chart.
2. Keep `Require breakout close` enabled and begin Bar Replay well before a
   recognizable structure.
3. Advance one candle at a time. Confirm no pivot/candidate appears until the
   configured right-pivot bars have closed.
4. Turn on forming patterns and debug mode. Verify the displayed prior trend is
   the state immediately before the first pivot, and inspect tolerance, slopes,
   geometry score, and rejection reason.
5. Cross the boundary by wick only, then by close. With the default setting only
   the close should confirm.
6. Replay the same interval twice and verify identical IDs, breakout bars, and
   no repeated same-signature labels.
7. Test sideways, trending, and high-volatility sessions; tune pivot length and
   ATR multipliers rather than adding price-level or percentage constants.
8. Review geometry first, then prior trend, classification, breakout accuracy,
   duplicate frequency, and false positives. Do not interpret detections as
   entries, exits, or evidence of profitability.
