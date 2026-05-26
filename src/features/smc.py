"""Smart Money Concepts — regras heurísticas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SwingPoint:
    index: int
    price: float
    kind: str  # "high" | "low"


def detect_swing_points(highs: list[float], lows: list[float], lookback: int = 3) -> list[SwingPoint]:
    swings: list[SwingPoint] = []
    n = len(highs)
    for i in range(lookback, n - lookback):
        if all(highs[i] > highs[i - k] and highs[i] > highs[i + k] for k in range(1, lookback + 1)):
            swings.append(SwingPoint(i, highs[i], "high"))
        if all(lows[i] < lows[i - k] and lows[i] < lows[i + k] for k in range(1, lookback + 1)):
            swings.append(SwingPoint(i, lows[i], "low"))
    return swings


def detect_fvg(highs: list[float], lows: list[float], closes: list[float]) -> list[tuple[int, str]]:
    """Fair Value Gaps — gap bullish/bearish em 3 velas."""
    gaps: list[tuple[int, str]] = []
    for i in range(2, len(closes)):
        if lows[i] > highs[i - 2]:
            gaps.append((i, "bullish"))
        if highs[i] < lows[i - 2]:
            gaps.append((i, "bearish"))
    return gaps
