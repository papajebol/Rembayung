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
assert '"Cup and Handle", "CUP", patternStart, patternEnd, TREND_UP' in text
assert '"Inverted Cup and Handle", "ICUP", patternStart, patternEnd, TREND_DOWN' in text
assert "f_normalizedSlope(b, c, barB, barC" in text
assert "f_normalizedSlope(c, d, barC, barD" in text
assert "float poleMove = poleEndPrice - poleStartPrice" in text
assert "f_windowRange(consolidationStart, consolidationEnd)" in text

print("PASS: repository Pine invariants (not a TradingView compiler test)")
