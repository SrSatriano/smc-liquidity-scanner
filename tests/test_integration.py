"""Integração scanner + mock WS + modelo heurístico."""

import pytest

from src.models.inference import LiquidityModel
from src.scanner.main import run


@pytest.mark.asyncio
async def test_run_three_ticks():
  import os

  os.environ["USE_MOCK_WS"] = "1"
  os.environ["MODEL_PATH"] = "models/missing.pt"
  os.environ["SIGNAL_THRESHOLD"] = "0.0"
  await run(max_ticks=3)


@pytest.mark.asyncio
async def test_pipeline_scores():
  from src.features.smc import detect_fvg, detect_swing_points
  from src.websocket.bybit import stream_trades

  model = LiquidityModel.load("models/missing.pt")
  async for candle in stream_trades("ETHUSDT", use_mock=True):
    swings = detect_swing_points(candle.highs, candle.lows)
    fvgs = detect_fvg(candle.highs, candle.lows, candle.closes)
    score = model.predict(candle.features)
    assert isinstance(swings, list)
    assert isinstance(fvgs, list)
    assert 0.0 <= score <= 1.0
    break
