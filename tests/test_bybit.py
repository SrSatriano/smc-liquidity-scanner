"""Testes do feed WebSocket (mock)."""

import pytest

from src.websocket.bybit import stream_trades


@pytest.mark.asyncio
async def test_mock_stream_yields_candles():
  count = 0
  async for candle in stream_trades("BTCUSDT", use_mock=True):
    assert len(candle.highs) >= 1
    assert len(candle.features) >= 3
    count += 1
    if count >= 3:
      break
  assert count == 3


@pytest.mark.asyncio
async def test_parse_kline_message():
  from src.websocket import bybit

  highs, lows, closes = [], [], []
  row = {"high": "51000", "low": "50900", "close": "50950", "volume": "12.5"}
  high = float(row["high"])
  low = float(row["low"])
  close = float(row["close"])
  volume = float(row["volume"])
  feats = bybit._features_from_ohlc(high, low, close, volume)
  highs.append(high)
  lows.append(low)
  closes.append(close)
  assert len(feats) == 8
  assert highs[-1] == 51000.0
