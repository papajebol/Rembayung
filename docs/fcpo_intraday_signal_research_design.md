# FCPO Intraday Signal Research Design

## Executive decision

The first system to research should be an **OHLC breakout/retest candidate generator with a microstructure meta-label that returns TAKE, SKIP, or WAIT**. It is the best fit for this feed because M5 bars define durable locations, while persistent changes in trade efficiency, top-book liquidity, flow, and Shadow states can confirm whether a release is being accepted without requiring complete exchange events or millisecond execution.

This is a research hypothesis, not a profitability claim. Every advanced version must beat its identical OHLC-only parent after realistic fees, slippage, latency, missed entries, and session-close liquidation.

## A. Available data map

| Source | Reliable role | Candidate features | Explicit non-use |
|---|---|---|---|
| M5 OHLC (0731/0771, 9d02/9d42) | Primary location, structure, volatility, and regime | confirmed swings; session high/low; range width; ATR/true range; compression percentile; breakout distance; retest depth; close location; trend slope | Do not reconstruct intrabar paths from OHLC or let incomplete bars leak into training. |
| 0080 TRADE | Persistent activity and price-response evidence | update rate; inter-arrival quantiles; `size_delta` quantiles; cumulative activity; price travel; net displacement; revisits; directional efficiency; impact per observed lot | Not complete Time & Sales, true aggressor flow, true CVD, or exchange-time sequencing. Negative/reset `cumvol` changes require explicit session/reset handling. |
| 0080 BOOK | Executable top-of-book state and liquidity asymmetry | spread; bid/ask quantities; imbalance; persistence; changes; refill/pull proxies; quote age | Not full DOM, exact cancellation, queue position, or sweep reconstruction. |
| 0080 FLOW | Vendor-state evidence learned empirically | levels, changes, persistence, acceleration, price divergence, interactions with TFI/absorption | No unsupported exchange-level interpretation of `avg`, `external`, or `internal`. |
| 1b70 OI | Slow participation/regime context | age-qualified OI level/change; price/OI quadrant; expansion/contraction | Never a fleeting trigger; stale values are missing or explicitly flagged, not carried forward indefinitely. |
| Shadow | Normalized microstructure states and transitions | TFI, absorption, acceptance, efficiency, momentum, refill/pull, large-update reaction | Events are features/confirmations, not standalone trades; definitions and thresholds must be versioned. |
| Dalian | Optional external regime/filter | lagged return; relative move; divergence; realized volatility; freshness | No presumed lead/lag and no use until aligned, stale-safe data proves incremental OOS value. |
| Timing metadata | Causal alignment and feed-health control | monotonic ordering; age; inter-arrival times; cross-stream as-of joins; gap/reset flags | Local receive time is not exchange event time. Arrival-time strategies must include live-computable delays. |

At decision time, all sources are joined **as of the local monotonic decision timestamp**. No later-arriving record may revise a historical feature. Feed age, gaps, crossed/invalid books, cumulative-volume resets, missing bars, and clock discontinuities are first-class quality fields. A stale or unhealthy feed should normally force `NO TRADE`.

## Common research and execution contract

### Baseline and costs

For each setup, freeze an OHLC-only rule before examining microstructure outcomes. Compare:

1. every OHLC candidate traded under the same entry/exit policy;
2. deterministic microstructure filtering;
3. a calibrated meta-model on the same candidates; and
4. optional OI/Dalian additions in ablations.

Use one fill simulator for all variants. A buy market order fills no better than the contemporaneous ask plus configured slippage; a sell fills no better than bid minus slippage. Limits fill only under a conservative, predefined touch/through rule, never merely because an OHLC bar contains the price. Include commissions, exchange/broker fees, bid-ask spread, empirical slippage by session/liquidity bucket, reaction delay, and mandatory end-of-session flattening. Reject an enhancement that raises classification accuracy but not after-cost utility.

### Candidate-level sampling and leakage controls

- The statistical unit is a **setup episode**, not every update. One episode begins at a causal OHLC trigger and ends at entry, expiry, invalidation, or a new independent setup. Cluster overlapping candidates and permit one decision per direction/location unless a documented reset occurs.
- Build bar structure only from bars closed by decision time. Compute rolling percentiles and thresholds using prior data only. Fit scalers, large-size thresholds, swing parameters, feature selection, probability calibration, and payoff choices inside each training fold.
- Purge overlapping label horizons around fold boundaries and embargo adjacent observations. Split chronologically by whole trading day; report day-clustered confidence intervals and block/bootstrap resampling rather than treating updates as independent.
- Preserve actual message arrival order and availability. Poll responses become usable only on receipt. Missing data and staleness must be represented exactly as live operation sees them.
- Freeze protocol parsing and Shadow-feature versions per experiment. Reprocessing is allowed only as a new version with a full rerun.

### Universal outcome panel

From the executable candidate entry price, calculate both long and short first-touch outcomes for a preregistered grid such as `+5/-5`, `+8/-5`, `+10/-5`, `+10/-8`, and `+15/-10` ticks, with horizons appropriate to intraday execution. Record MFE, MAE, time to MFE/MAE, time to target/stop, first touch, neither-touched expiry, realized exit, and net P&L after costs at 15, 30, 60, 120, and 300 seconds. Same-update target/stop ambiguity must use event ordering when observed and otherwise a conservative adverse-first convention.

The primary metric is mean net P&L per candidate and per taken trade, with a day-clustered 95% confidence interval. Secondary metrics are trade count, exposure time, win probability, target-before-stop probability, payoff distribution, profit factor, MAE/MFE, maximum and expected drawdown, losing streak, calibration, coverage, and stability by morning/afternoon/night session, volatility, trend/range, spread/liquidity, OI state, calendar period, and contract/roll proximity.

## B. Ranked signal architectures

## 1. Breakout/retest acceptance meta-label — most promising and simplest

**Implementation style:** deterministic OHLC state machine plus logistic regression or small gradient-boosted meta-classifier. The OHLC setup creates candidates; the model selects `TAKE`, `SKIP`, or `WAIT`.

1. **Core idea.** Exploit continuation after a genuine escape from a well-defined M5 consolidation. Microstructure is not asked to predict direction from nowhere; it distinguishes accepted release from thin, inefficient, or absorbed breakout activity.
2. **Price/OHLC condition.** Using only completed M5 bars, define a causal compression box (for example, prior-bar range/ATR and realized-range percentiles learned in training), minimum touches or residence, and a close outside the box by a volatility-normalized buffer. The OHLC baseline enters the breakout or its first retest. Long and short rules are symmetric. Avoid candidates too close to mandatory session flattening.
3. **Microstructure condition.** In fixed pre-break, break, and post-break windows use trade pace and its change, size distribution, observed directional efficiency, displacement, revisits, impact per observed activity, spread, persistent book imbalance, refill/pull proxies, FLOW changes, and Shadow TFI/acceptance/absorption/momentum states. Favor a long when upward result per effort rises, ask refill weakens or ask liquidity pulls, buying produces displacement, and the break holds; reverse for shorts. A single event is insufficient.
4. **State transition.** `compression/high effort-low result -> repeated boundary tests/absorption -> opposing liquidity deterioration -> directional efficiency and displacement expansion -> acceptance outside -> optional retest hold`. The transition and persistence matter more than absolute thresholds.
5. **Signal timing.** Human-practical default: after an M5 close outside, wait up to 30–120 seconds for persistent acceptance, then enter on a shallow retest/hold or continued tradeable progression. `WAIT` has an expiry; a runaway price beyond the maximum chase distance becomes `SKIP`.
6. **Invalidation.** A close or persistent trade back inside the box beyond a trained buffer, opposite absorption/efficiency transition, spread/data-health failure, or setup timeout invalidates the candidate.
7. **Entry method.** Prefer a structural zone around the broken boundary and observed spread. Use a marketable limit after acceptance or a conservative limit on the first retest; separately evaluate breakout market entry. Do not assume fills at the breakout print.
8. **Stop logic.** Place the logical stop beyond the retest failure/box boundary plus a volatility and spread buffer. Select the buffer from training-fold MAE distributions subject to a maximum risk budget; size from stop distance. If a viable structural stop is too wide, skip rather than tighten arbitrarily.
9. **Target/exit logic.** Compare next structure/range projection and empirically supported target-stop pairs. Partial/time exits are included only if OOS net expectancy improves. Exit on target, stop, expiry, opposite acceptance transition, or mandatory flattening. Select using target-before-stop and full payoff distributions, not win rate alone.
10. **Data required.** Required: completed M5 OHLC, TRADE, BOOK, timestamps/feed health. Candidate additions: FLOW and Shadow. OI is a slow stratification/filter. Dalian is held out initially.
11. **How to test.** Each causal compression break is one episode. Label executable entry opportunities by first-touch outcomes and realized delayed-entry P&L; censor/record no-fill and expiry. Use chronological discovery, untouched OOS, then rolling walk-forward with purging and day bootstrap intervals. Compare identical candidates and exits against the OHLC breakout/retest baseline. Report the universal metrics, session/regime stability, and feature-family ablations.
12. **Failure mode.** The compression definition may be overfit; many overlapping snapshots may inflate sample size; vendor bundling can make pace/size artifacts look predictive; a retest limit may be unrealistically filled; fast releases may be missed; structural edges may vanish after spread and slippage. Regime or contract-specification changes can break fixed tick thresholds.

## 2. Trend-pullback exhaustion and resumption

**Implementation style:** regime model plus deterministic transition or calibrated conditional-probability model.

1. **Core idea.** Join an established intraday M5 trend after a countertrend pullback loses result despite continued effort, then order flow and price efficiency rotate back with the trend.
2. **Price/OHLC condition.** Define trend causally using higher highs/lows or lower highs/lows, slope, and price relative to an anchored session reference. Require a pullback into prior breakout, swing, or volatility-normalized value zone without structural trend failure. The OHLC baseline buys/sells the first qualifying rejection/resumption bar.
3. **Microstructure condition.** For a long, the pullback shows sell TFI/flow or activity but shrinking downside displacement, `SELLERS_ABSORBED`/`LOW_IMPACT_SELL`, bid persistence/refill, and repeated low failures. Confirmation is rising buy efficiency/momentum, positive TFI transition, and no persistent ask-heavy veto. Reverse for shorts.
4. **State transition.** `trend impulse -> orderly pullback -> countertrend effort with declining result -> absorption at structure -> with-trend efficiency/impact expansion`. Static bid heaviness alone is not a trigger.
5. **Signal timing.** Use M5 to establish trend/location, then wait 30–120 seconds for exhaustion plus resumption. Enter only after a tradeable price reclaim or local micro-range break, not on the first absorption flag.
6. **Invalidation.** The structural swing fails, countertrend activity gains efficiency and acceptance, the pullback exceeds its duration/depth envelope, or the broader trend regime disappears.
7. **Entry method.** Marketable limit after the reclaim, or a limit in the reclaimed structural zone with short expiry. Compare with entry on the next M5 open for the baseline.
8. **Stop logic.** Beyond the pullback extreme/structural failure plus spread-volatility allowance, calibrated against setup-specific MAE. Reject trades whose structure-implied risk violates the daily/per-trade budget.
9. **Target/exit logic.** Prior impulse extreme is the first structural objective; extension is conditional on OOS continuation probability. Test fixed first-touch grids, trailing behind completed M5 swings, and time exit when resumption does not progress.
10. **Data required.** M5 OHLC, TRADE, BOOK, Shadow, timing; FLOW is useful. Fresh OI may stratify participation. Dalian is optional and tested last.
11. **How to test.** One episode per pullback into a predeclared zone, deduplicated until trend resumes or fails. Labels start at feasible confirmation entry and include target-before-stop, MFE/MAE, time-to-event, and net returns. Use discovery/OOS/walk-forward, day-block bootstrap, regime/session slices, and direct comparison with the OHLC trend-pullback baseline.
12. **Failure mode.** A reversal can masquerade as exhaustion; trend filters are highly parameter-sensitive; confirmation enters too late and destroys reward/risk; Shadow states may merely restate price; favorable limit assumptions and hindsight swing identification can manufacture returns.

## 3. Failed-auction reversal at session extremes or range edges

**Implementation style:** interpretable score/state machine first; later calibrated classifier or survival model.

1. **Core idea.** Fade a probe beyond an established session high/low or range edge when substantial directional effort fails to gain acceptance and the opposite side begins producing greater price result.
2. **Price/OHLC condition.** A completed-bar-defined session extreme, prior swing, or mature range edge is probed beyond by a minimum tick/volatility buffer, then price returns into the prior area. Levels must exist before the probe. The OHLC baseline trades the failed breakout/rejection.
3. **Microstructure condition.** At an upside failure: buy-oriented TFI/FLOW and high activity coexist with low upward impact, repeated highs, `BUYERS_ABSORBED`/`LARGE_BUY_ABSORBED`, persistent ask refill, then bid pull/ask-heavy state, sell efficiency and downward momentum. Mirror at lows. Require spread and quote quality to remain tradeable.
4. **State transition.** `probe with directional effort -> no acceptance/repeated rejection -> absorbing liquidity persists -> initiating side exhausts -> opposite-side efficiency expands -> re-entry into range`.
5. **Signal timing.** Wait for both structural re-entry and a persistent opposite transition. A limit blindly placed at the extreme is not the research default. Allow enough persistence for human response and skip if most expected move is already gone.
6. **Invalidation.** Renewed acceptance beyond the extreme, fresh high/low accompanied by efficient directional progress, absorbing liquidity disappears, or price fails to rotate within a fixed time.
7. **Entry method.** Marketable limit on re-entry/retest of the failed boundary, or pullback after the first opposite micro-range break. Compare both against next-bar OHLC entry.
8. **Stop logic.** Beyond the failed-auction extreme plus spread/volatility buffer. Use conditional MAE and gap/slippage tails; cap risk and skip anomalously wide probes.
9. **Target/exit logic.** First target is range midpoint/nearest internal structure; far edge is conditional. Optimize no arbitrary ratio: estimate target-before-stop and time-to-target for each structural destination, include time stops, and test exit if rejection evidence reverses.
10. **Data required.** M5 OHLC, TRADE, BOOK, Shadow, timestamps; FLOW is valuable. OI may identify participation on the probe but must be fresh. Dalian divergence is experimental.
11. **How to test.** Episodes begin with the first qualifying probe of a pre-existing edge and lock out repeated probes until reset. Label from executable post-confirmation entries. Compare with the OHLC failed-breakout baseline using purged chronological splits, walk-forward, block bootstrap, after-cost distributions, MFE/MAE, frequency, drawdown, and stability by trend/range and session.
12. **Failure mode.** Strong trend days repeatedly punish fades; the session extreme may be defined with future data; multiple tests create dependence; absorption rules can fire because updates are missing; stop slippage is worst exactly when the failure becomes a true breakout.

## 4. Compression directional-release survival/ranking model — experimental

**Implementation style:** competing-risk survival model or gradient-boosted ranking model over pre-release snapshots.

1. **Core idea.** During a balanced M5 range, estimate whether upside target, downside target, or no release will occur first—and when—before an obvious bar breakout. This directly addresses whether microstructure identifies control before visible expansion.
2. **Price/OHLC condition.** Only mature, causally defined compressions with sufficient residence, narrowing realized range, several price revisits, and room to the next structure qualify. The OHLC baseline enters only after a conventional consolidation breakout.
3. **Microstructure condition.** Multi-window (5/15/30/60-second) changes in pace, size, directional efficiency, impact, revisits, TFI/FLOW persistence, absorption asymmetry, bid/ask persistence, refill/pull imbalance, spread, and Shadow transitions. OI and Dalian are context covariates, never required triggers.
4. **State transition.** Model trajectories from symmetric low-efficiency balance toward asymmetric absorption, weakening liquidity on one side, rising opposite-side impact, pace acceleration, and directional release. A sequence representation can be engineered transition summaries before attempting any complex sequence learner.
5. **Signal timing.** Recompute at human-compatible intervals such as 5–15 seconds. Usually output `WAIT`; enter only when calibrated directional first-touch probability and expected value cross frozen thresholds for multiple observations. A price-confirmed variant waits for the range edge; a pre-break variant must demonstrate enough extra payoff to justify greater false-break risk.
6. **Invalidation.** Probability/EV falls below threshold, direction flips, compression expires, structure breaks opposite, data becomes stale, or price moves beyond the permitted entry zone.
7. **Entry method.** Marketable limit near the favored edge after persistent state change, or first shallow pullback after release. Never require capture of the initial millisecond impulse.
8. **Stop logic.** Opposite side/center of the compression depending on learned MAE and entry location; include a time stop because the hypothesis predicts near-term release. Structural validity and risk limits override model confidence.
9. **Target/exit logic.** Use the survival/competing-risk estimates for target-before-stop within horizon, but execute simple frozen structural exits. Re-estimation can justify early exit only after separately proving net benefit after turnover costs.
10. **Data required.** M5 OHLC, TRADE, BOOK, FLOW, Shadow, synchronized timing and quality fields. Fresh OI and aligned Dalian are optional ablations.
11. **How to test.** Sample one decision grid per independent compression, weight/cluster snapshots within episodes, and evaluate both candidate-level ranking and an explicit threshold policy. Labels are upside-first, downside-first, or censored/no-event with time to touch. Use nested chronological tuning, untouched OOS, rolling walk-forward, calibration/Brier and survival calibration, day bootstrap, after-cost policy metrics, MFE/MAE, drawdown, and session/regime stability. Compare against the later OHLC consolidation breakout and against no trade.
12. **Failure mode.** Snapshot autocorrelation creates false sample size; pre-break direction may be intrinsically noisy; vendor update batching can dominate pace; censoring and overlapping horizons may be mishandled; repeated rescoring creates hidden turnover; a sophisticated model can overfit changing feed behavior and be less robust than waiting for price.

## Architecture ranking and research order

1. **Breakout/retest acceptance meta-label:** clearest causal location, modest modeling burden, practical timing, and a strong like-for-like OHLC baseline.
2. **Trend-pullback exhaustion/resumption:** common opportunity and interpretable transition, but trend and pullback definitions add degrees of freedom.
3. **Failed-auction reversal:** compelling effort-versus-result expression, but adverse tails on trend days demand strict regime controls.
4. **Pre-release survival/ranking:** most direct answer to early control, but most exposed to dependence, overfit, and feed artifacts.

## C. Top recommendation

Start with **Architecture 1: breakout/retest acceptance meta-label**.

- M5 price defines the place and direction, so incomplete vendor events do not bear the full forecasting burden.
- Confirmation can persist for tens of seconds and support a price zone, making reaction latency and semi-systematic execution realistic.
- TAKE/SKIP/WAIT tests the likely highest-value role for microstructure: rejecting poor OHLC trades and improving entry quality rather than manufacturing many new trades.
- The effort-versus-result hypothesis has observable, falsifiable transitions: pre-break activity with low result followed by directional efficiency/impact expansion and acceptance.
- The baseline is natural and economically fair. If microstructure cannot improve the same breakout/retest candidates after costs, it should not be retained.
- An interpretable logistic model can establish incremental value with limited data. Boosted trees are justified only after adequate episode counts and repeatable nonlinear lift; deep learning is not justified initially.

## D. Exact first experiment

### Preregistered hypothesis

Among causal M5 compression breakouts, a persistent post-break acceptance state improves after-cost expectancy and reduces false breakouts versus trading every OHLC breakout at the same delayed decision opportunity.

### Setup and OHLC condition

1. Use one continuous/active FCPO contract policy fixed before testing, with explicit roll-day treatment.
2. On each completed M5 bar, consider the preceding six completed bars a candidate box.
3. Require box width to be at or below the rolling 20th percentile of six-bar widths over prior sessions, and the last six bars' mean true range at or below the rolling 30th percentile. Estimate percentiles using training/past data only.
4. Require at least two prior intrabar high/low contacts within one tick (or a training-frozen volatility-scaled tolerance) of the relevant edge, to avoid a one-print box.
5. A breakout candidate occurs when a completed M5 bar closes at least one tick beyond the box. Freeze one-tick initially; robustness tests vary it without selecting on OOS.
6. Exclude overlapping boxes, lock out the same direction until retest/failure/reset, require a valid spread, and require enough time before session close for the 300-second horizon and flattening.

The **OHLC baseline** acts at the identical earliest live decision time after the breakout close and enters at the first executable quote, subject to the same maximum chase distance, stop, target, time exit, and costs. A secondary named baseline enters on the first retest; do not mix baseline definitions after seeing results.

### Microstructure observation and candidate timing

Observe the final 60 seconds before the breakout close and up to 60 seconds after it. At 15, 30, and 60 seconds after the close, make causal decisions using only messages received by that timestamp:

- `TAKE` at the first checkpoint whose calibrated net-EV estimate is positive beyond a training-selected margin and whose direction is stable at two consecutive 5-second calculations;
- `WAIT` while no checkpoint qualifies and structure remains valid;
- `SKIP` at 60 seconds, on invalidation, feed-health failure, or excessive chase distance.

The baseline also enters at the checkpoint selected by a rule fixed without future microstructure—for the primary comparison, 30 seconds—so any gain is not silently due to giving the advanced model a different fill opportunity. Additionally report a policy-level comparison in which WAIT/SKIP are allowed, with opportunity costs and no-fill rates.

### Initial feature set

Keep the first model small and direction-normalized (positive means favorable to breakout):

- box width/ATR, breakout close distance, breakout-bar range and close location;
- TRADE update rate and acceleration (pre-60 versus latest 15 seconds), observed activity, median/p90 `size_delta`, net displacement, total travel, revisits, directional efficiency, and impact per observed lot;
- median/current spread, book imbalance mean and persistence, favorable-liquidity pull and opposing refill persistence;
- `tfi5`, `tfi15`, their change/persistence, directional `buy5-sell5`, `momentum5`;
- counts/durations of accepted, absorbed, low-impact, refill, pull, and high-efficiency Shadow states, direction-normalized;
- FLOW level/change/persistence only as empirically named raw/vendor features;
- message ages, gap flags, time of day, and volatility bucket.

Do **not** include OI or Dalian in the first model. Add each later as a separately locked ablation. This prevents a simple question from becoming an uncontrolled feature search.

### Outcome and model

- Primary label: from the executable ask/bid at each checkpoint, whether `+8 ticks` is touched before `-5 ticks` within 300 seconds, with neither touched recorded as censored/timeout and a fixed time-exit return.
- Primary economic outcome: realized ticks under that complete policy minus measured spread, commissions/fees, and conservative empirical slippage.
- Secondary labels: the universal target/stop grid, MFE/MAE at all prescribed horizons, time to touch, and breakout acceptance (remaining outside the box).
- Initial model: regularized logistic regression predicting target-before-stop, with probability calibration fitted within training folds. Convert probability to expected value using empirical conditional win/loss/timeout payoffs and costs. Compare against a simple frozen transition score. Only then consider shallow boosted trees.

### Sample and no-lookahead design

- One independent breakout episode is one row per prespecified checkpoint for modeling, with episode weights so a setup contributes total weight one. Policy evaluation produces one trade decision per episode.
- Use the earliest chronological block for discovery, a following validation block for all thresholds/payoff decisions, and a final untouched OOS block. Then run anchored or rolling walk-forward retraining by whole session/day.
- Purge episodes whose 300-second labels overlap split boundaries; embargo adjacent periods. Fit rolling percentiles, imputation, scaling, feature selection, model, calibration, and TAKE threshold inside training data.
- Recreate arrival-time joins from monotonic timestamps. Never backfill late BOOK/FLOW/OI responses. Treat feed gaps as observed quality states or exclusion rules fixed in training.

### Metrics and decision thresholds

Report baseline and advanced policy trade count, coverage/skip rate, net expectancy per candidate and per trade, total net P&L, win probability, target-before-stop, timeout rate, MAE/MFE, time to target/stop, profit factor, drawdown, losing streak, calibration, and results by session, volatility, direction, year/month, and spread bucket. Use a day-level stationary/block bootstrap for 95% confidence intervals and preserve serial dependence.

**Success criterion:** on untouched OOS and the aggregate walk-forward test, the advanced policy has positive after-cost expectancy; its day-block 95% interval for incremental net P&L per OHLC candidate versus baseline excludes zero; it retains a preregistered minimum frequency (for example at least 30% of baseline candidates and enough independent trades for each major session report); and no single session/regime or small group of days supplies most profits. It should also improve at least one practical dimension—MAE, drawdown, or false-break rate—without unacceptable frequency loss.

**Failure criterion:** reject or simplify if net expectancy is non-positive, incremental confidence interval includes zero after the predetermined sample, gains disappear under one-tick-worse fills/reaction delays, calibration is poor, frequency is unusable, ablation shows the model only restates OHLC, or performance is concentrated/unstable. A failed result is useful evidence to deploy the OHLC baseline or no trade rather than add complexity.

## E. Complete live signal path

1. **Ingest live Wenhua data.** Normalize contract/tick size/session, preserve raw records, order by monotonic receipt, and expose freshness and reset/gap health.
2. **Build price structure.** Finalize causal M5 bars and derive swings, compression boxes, trend/range, volatility, session levels, and structural room.
3. **Create candidate setup.** OHLC alone emits a versioned candidate with direction, zone, structural invalidation, expiry, and baseline action.
4. **Measure microstructure state.** Maintain fixed rolling windows for effort, result, book persistence, FLOW, and Shadow states. Join OI/Dalian only as stale-safe, previously validated context.
5. **Decide TAKE/SKIP/WAIT.** Apply hard data/risk vetoes, then a calibrated candidate model or deterministic transition. Log all candidates and all three decisions to prevent selection bias.
6. **Construct entry.** Publish a tradeable price area, current spread, maximum chase price, order style, and expiry. Estimate the achievable fill after human/system delay.
7. **Define invalidation and stop.** Structural failure is stated before entry. Translate it into a stop using spread, volatility, gap/slippage tails, and setup-specific MAE; risk-size the position and enforce daily limits.
8. **Define target and exit.** Select only research-supported structural/first-touch targets and time exits. Flatten before the applicable FCPO session close and never carry overnight.
9. **Publish quality.** Report calibrated probability range, expected net ticks/currency after cost, evidence/feature-family contributions, regime, feed quality, and OOS support count—not an unqualified confidence adjective.
10. **Capture outcomes.** Store decision-time features, model/version, quotes, intended and simulated/actual fills, latency, modifications, exit reasons, MFE/MAE, and all skipped candidates.
11. **Monitor and validate.** Compare live calibration, feature distributions, fill slippage, frequency, and expectancy with walk-forward expectations. Degrade to `NO TRADE` on data health or material drift; retraining never overwrites historical predictions.
12. **Render practical output.** The signal is concise and zone-based, for example:

```text
LONG
Entry area: broken M5 box edge to +2 ticks; max chase +4 ticks
Invalidation: sustained return inside box / acceptance transition lost
Stop: beyond retest low and structural buffer (risk-sized)
Target: next structure; 8-before-5 research policy; mandatory time/session exit
Signal quality: calibrated 0.64 target-before-stop; positive estimated net EV; adequate OOS support
Market structure: six-bar compression, close above range, first retest holding
Microstructure reason: pace and upward efficiency expanded; ask refill weakened; acceptance persisted
Context: normal spread/volatility; fresh feed; OI/Dalian not used
```

Otherwise output `NO TRADE` with a reason such as no structural candidate, awaiting confirmation, invalidated, stale feed, excessive chase, insufficient expected value, risk limit, or session cutoff.

## F. Priority rules

1. Validate data semantics, causality, and fill assumptions before forecasting.
2. Establish the OHLC-only economic baseline before opening microstructure feature selection.
3. Test whether persistent microstructure transitions improve selection and execution of that same candidate set.
4. Prefer parsimonious, calibrated, explainable models; complexity earns deployment only through stable incremental OOS after-cost value.
5. Add OI and Dalian one at a time and retain them only for demonstrable incremental value.
6. Optimize the full policy—candidate, decision, fill, risk, exit, and abstention—not a next-tick classifier.
7. Treat `NO TRADE` as a primary valid outcome and profitability as an empirical result, never an assumption.
