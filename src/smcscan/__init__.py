"""Scanner de Smart Money Concepts (estrutura, FVG, order blocks e liquidez)."""

from .analysis import Candle, Report, analyze, stats

__all__ = ["Candle", "Report", "analyze", "stats"]
__version__ = "1.1.0"
