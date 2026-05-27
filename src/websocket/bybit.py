"""Feed Bybit V5 (kline) com fallback simulado."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import AsyncIterator

logger = logging.getLogger(__name__)


@dataclass
class Candle:
  highs: list[float]
  lows: list[float]
  closes: list[float]
  features: list[float] = field(default_factory=list)


def _features_from_ohlc(high: float, low: float, close: float, volume: float) -> list[float]:
  spread = (high - low) / close if close else 0.0
  return [
    close / 100_000.0,
    spread,
    volume / 1_000.0,
    high / 100_000.0,
    low / 100_000.0,
    (high + low) / 2 / 100_000.0,
    1.0 if close >= (high + low) / 2 else 0.0,
    spread * volume,
  ]


async def _mock_stream(symbol: str) -> AsyncIterator[Candle]:
  i = 0.0
  while True:
    i += 1
    base = 50_000.0 + (i % 100)
    h, l, c = base + 10, base - 10, base
    vol = 10.0 + (i % 5)
    yield Candle([h], [l], [c], _features_from_ohlc(h, l, c, vol))
    await asyncio.sleep(0.05)


async def _bybit_kline_stream(symbol: str, ws_url: str) -> AsyncIterator[Candle]:
  import websockets

  topic = f"kline.1.{symbol}"
  subscribe = {"op": "subscribe", "args": [topic]}
  history_highs: list[float] = []
  history_lows: list[float] = []
  history_closes: list[float] = []

  async with websockets.connect(ws_url, ping_interval=20) as ws:
    await ws.send(json.dumps(subscribe))
    logger.info("Bybit WS subscribed: %s", topic)

    async for raw in ws:
      msg = json.loads(raw)
      if msg.get("topic") != topic:
        continue
      rows = msg.get("data") or []
      if not rows:
        continue
      row = rows[0] if isinstance(rows, list) else rows
      high = float(row.get("high", 0))
      low = float(row.get("low", 0))
      close = float(row.get("close", 0))
      volume = float(row.get("volume", 0))
      if close <= 0:
        continue

      history_highs.append(high)
      history_lows.append(low)
      history_closes.append(close)
      window = int(os.getenv("CANDLE_WINDOW", "20"))
      if len(history_highs) > window:
        history_highs = history_highs[-window:]
        history_lows = history_lows[-window:]
        history_closes = history_closes[-window:]

      feats = _features_from_ohlc(high, low, close, volume)
      yield Candle(
        list(history_highs),
        list(history_lows),
        list(history_closes),
        feats,
      )


async def stream_trades(
  symbol: str,
  *,
  ws_url: str | None = None,
  use_mock: bool | None = None,
) -> AsyncIterator[Candle]:
  """Stream de candles: mock, Bybit WS ou fallback automático."""
  url = ws_url or os.getenv(
    "BYBIT_WS_URL",
    "wss://stream.bybit.com/v5/public/linear",
  )
  mock = use_mock if use_mock is not None else os.getenv("USE_MOCK_WS", "0").strip() in (
    "1",
    "true",
    "yes",
  )

  if mock:
    async for candle in _mock_stream(symbol):
      yield candle
    return

  try:
    async for candle in _bybit_kline_stream(symbol, url):
      yield candle
  except Exception as exc:
    logger.warning("Bybit WS falhou (%s); usando mock.", exc)
    async for candle in _mock_stream(symbol):
      yield candle
