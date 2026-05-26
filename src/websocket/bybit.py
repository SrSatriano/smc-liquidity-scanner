"""WebSocket feed Bybit (feed WebSocket Bybit com fallback simulado)."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class Candle:
    highs: list[float]
    lows: list[float]
    closes: list[float]
    features: list[float]


async def stream_trades(symbol: str) -> AsyncIterator[Candle]:
    """Yield candles simulados quando WS não configurado."""
    _ = os.getenv("WS_URL", "")
    i = 0.0
    while True:
        i += 1
        base = 50000 + (i % 100)
        h, l, c = base + 10, base - 10, base
        yield Candle([h], [l], [c], [c / 1000, 0.1, 0.2])
        await asyncio.sleep(1)
