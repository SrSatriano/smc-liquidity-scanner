"""SMC Liquidity Scanner — entry point."""

from __future__ import annotations

import asyncio
import logging
import os

from src.config import load_settings
from src.features.smc import detect_fvg, detect_swing_points
from src.models.inference import LiquidityModel
from src.websocket.bybit import stream_trades

logging.basicConfig(
  level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
  format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def run(max_ticks: int | None = None) -> None:
  cfg = load_settings()
  model = LiquidityModel.load(cfg.model_path)
  logger.info(
    "Scanner %s | modelo=%s | mock_ws=%s",
    cfg.symbol,
    model.mode,
    cfg.use_mock_ws,
  )

  n = 0
  async for candle in stream_trades(
    cfg.symbol,
    ws_url=cfg.ws_url,
    use_mock=cfg.use_mock_ws,
  ):
    swings = detect_swing_points(candle.highs, candle.lows)
    fvgs = detect_fvg(candle.highs, candle.lows, candle.closes)
    score = model.predict(candle.features)
    if score >= cfg.signal_threshold:
      logger.info(
        "[SIGNAL] %s score=%.2f swings=%d fvgs=%d",
        cfg.symbol,
        score,
        len(swings),
        len(fvgs),
      )
    n += 1
    if max_ticks is not None and n >= max_ticks:
      break


def main() -> None:
  ticks = os.getenv("MAX_TICKS")
  max_ticks = int(ticks) if ticks else None
  asyncio.run(run(max_ticks=max_ticks))


if __name__ == "__main__":
  main()
