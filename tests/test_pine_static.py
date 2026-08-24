#!/usr/bin/env python3
"""Repository-side invariants; these do not replace TradingView compilation."""

from pathlib import Path
import re

SOURCE = Path(__file__).parents[1] / "fcpo_25_core_patterns_v1.pine"
text = SOURCE.read_text()

assert "//@version=6" in text
assert "indicator(" in text
assert "strategy(" not in text
assert "lookahead_on" not in text

families = [
    "Double Top", "Double Bottom", "Triple Top", "Triple Bottom",
    "Head and Shoulders", "Inverse Head and Shoulders", "Rounding Top",
    "Rounding Bottom", "Diamond Top", "Diamond Bottom", "V-Top", "V-Bottom",
    "Megaphone / Broadening", "Bump and Run Top", "Bump and Run Bottom",
    "Rising Wedge", "Falling Wedge", "Ascending Triangle", "Descending Triangle",
    "Symmetrical Triangle", "Bullish Flag", "Bullish Pennant", "Rectangle",
    "Cup and Handle", "Continuation Diamond",
]
assert not [family for family in families if family not in text]

# The original compiler failure was an NA-initialized chained declaration.
assert not re.search(r"\b(?:float|int|bool|string|line|label)\s+\w+\s*=\s*na\s*,", text)
assert not re.search(r"(?m)^\s*\w+\s*=\s*na\s*$", text)

assert "f_lineValueAt(" in text
assert "moreExtreme" in text and "array.set(pivotPrices" in text
assert "highExcursion" in text and "lowExcursion" in text
assert "label.new(bar_index, close, code + \" FORMING" in text
assert "f_deleteForming(candidate)" in text
assert "ta.highest" not in text and "ta.lowest" not in text

# Breakout lifecycle must consume candidate boundaries, not a stored midpoint.
lifecycle = text[text.index("// Candidate lifecycle"):]
assert "f_boundaryUpper(candidate, bar_index)" in lifecycle
assert "f_boundaryLower(candidate, bar_index)" in lifecycle
assert "localHi" not in lifecycle and "localLo" not in lifecycle

# Candidate storage is a single typed object array: push/shift cannot desynchronize.
assert "array<PatternCandidate> candidates" in text
assert "array.push(candidates, proposed)" in text
assert "PatternCandidate removed = array.shift(candidates)" in text

# Explicitly guard the repaired geometry and context defects.
assert "upperSlope < lowerSlope and lowerSlope < 0.0" in text
assert "lowerSlope > upperSlope and upperSlope > 0.0" in text
assert '"Cup and Handle", "CUP", leftRimBar, handleBar, TREND_UP' in text
assert '"Inverted Cup and Handle", "ICUP", leftRimBar, handleBar, TREND_DOWN' in text
assert "f_equalLevel(leftRim, rightRim, cupATR)" in text
assert "f_normalizedSlope(b, c, barB, barC" in text
assert "f_normalizedSlope(c, d, barC, barD" in text
assert "float poleMove = poleEndPrice - poleStartPrice" in text
assert "f_windowRange(consolidationStart, consolidationEnd)" in text

# Selectivity added after initial TradingView validation.
assert "minWedgeContractionRatio" in text and "contractionRatio >= minWedgeContractionRatio" in text
assert "minWedgeBars" in text and "patternBars >= minWedgeBars" in text
assert "maxApexDistanceMultiple" in text and "apexValid" in text
assert "vertexMinFraction" in text and "vertexMaxFraction" in text
assert "leftCurveSlope > 0.0 and rightCurveSlope < 0.0" in text
assert "leftCurveSlope < 0.0 and rightCurveSlope > 0.0" in text
assert "minRoundingHeightATR" in text
assert "projectedFinalBoundary" in text and "finalPivotValid" in text
assert "f_clusterMatch(" in text and "displayClusterOverlap" in text
assert 'input.string("Latest Only", "Drawing Mode"' in text
assert 'drawingMode == "Latest Only"' in text
assert "neckBar1" in text and "neckAtBreakout" in text
assert "ambiguousBreakout" in text and "ambiguousBreakout ? 0" in text
assert "minDoubleDepthATR" in text and "doubleDepthATR >= minDoubleDepthATR" in text
assert "minVLegATR" in text and "leftAmplitudeATR >= minVLegATR" in text
assert "trendPersistence" in text and "priorPersistence >= minPriorTrendBars" in text
assert "candidate.geometryScore * 0.50" in text
assert not re.search(r"f_clamp\((?:6[5-9]|7\d|8\d)(?:\.0)?\s*\+", text)

# Round 3 lifecycle, final-quality, frozen-tolerance, and morphology guards.
assert 'minGeometryScore = input.int(55' in text
assert 'minFinalQuality = input.int(60' in text
assert "geometryScore >= minGeometryScore or showLow" in text
assert "finalQualityAccepted = quality >= minFinalQuality or showLow" in text
assert "if not finalQualityAccepted" in text
assert "STATUS_CONFIRMED_INTERNAL" in text
assert "STATUS_CONFIRMED_SUPPRESSED" in text
assert "STATUS_CONFIRMED_EMITTED" in text
assert "first-confirmed-wins" in text
assert "confirmed cluster already emitted" in text
assert "array.remove(displayedPatterns" not in text
assert "label.delete(clustered" not in text
assert "confirmedEventCounter += 1" in text
assert "confirmedEventCounter > confirmedEventCounter[1]" in text
assert "dashboardWinner" in text and "bestQualityThisBar" in text
assert "if invalidated or expired" in text
assert text.index("if invalidated or expired") < text.index("else if direction != 0 and strengthAccepted")
assert 'input.string("Wick", "Invalidation Mode"' in text
assert "same-bar structural invalidation" in text
assert "windowHigh + f_tolerance(patternATR)" in text
assert "windowLow - f_tolerance(patternATR)" in text
assert "minRoundingCenterEdgeATR" in text and "topCenterDominant" in text
assert "slopeConsistencyPoints" in text
assert "minPennantContractionRatio" in text
assert "minPennantStartWidthATR" in text
assert "minFlagRangeATR" in text
assert '"All (max 50)"' in text
assert "touchStructurePoints" in text
assert "Relax Cup Curve Fit" in text and "allowVCup" not in text
assert "toleranceAtCreation" in text
assert "toleranceAtBreakout" in text
assert "duplicateTolerance" in text and "clusterTolerance" in text
assert "priorStructureComponent" in text
assert "priorSlopeComponent" in text
assert "priorEMAComponent" in text
assert "priorPersistenceComponent" in text

# Round 4 confirmation-gap, apex, cleanup, and compact-geometry guards.
assert "f_confirmationGapInvalidated(" in text
assert "for gapBar = endBar + 1 to bar_index" in text
assert "confirmation-gap invalidation" in text
assert "confirmation-gap opposite-boundary break" in text
assert "gapHistoryAvailable and not gapInvalidated" in text
assert "f_expiresAtBoundaryCross(" in text
assert "expiresAtBoundaryCross" in text
assert "upperBoundary <= lowerBoundary" in text
assert "pattern apex passed" in text
assert "candidate.expectedBreakout == BREAK_BILATERAL and bullishBreak and bearishBreak" in text
assert "not requireClose and candidate.expectedBreakout" not in text
assert "oldCandidate.status == STATUS_FORMING and similar" in text
assert "cleanupCandidate.status != STATUS_FORMING" in text
assert "array.remove(candidates, resolvedIndex)" in text
assert "minDoubleSeparationBars" in text and "maxDoubleSeparationBars" in text
assert "doubleSeparationValid" in text
assert "minTripleLegBars" in text and "maxTripleSpanBars" in text
assert "tripleSpacingValid" in text
assert "flagWidthsPositive" in text and "flagWidthChangeRatio" in text
assert "maxFlagWidthChangeRatio" in text
assert "minDiamondBars" in text and "minDiamondMaxWidthATR" in text
assert "finalContractionValid" in text and "diamondSizeValid" in text
assert "minHandleBars" in text and "maxHandleDurationRatio" in text
assert "cupChronologyValid" in text and "handleDurationValid" in text
assert 'input.bool(true, "Show confirmed labels"' in text

print("PASS: repository Pine invariants (not a TradingView compiler test)")
