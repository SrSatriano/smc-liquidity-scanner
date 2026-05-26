"""SMC Liquidity Scanner — entry point."""

from __future__ import annotations

import asyncio
import os

from src.features.smc import detect_fvg, detect_swing_points
from src.models.inference import LiquidityModel
from src.websocket.bybit import stream_trades


async def run() -> None:
    symbol = os.getenv("SYMBOL", "BTCUSDT")
    model = LiquidityModel.load(os.getenv("MODEL_PATH", "models/best.pt"))

    async for candle in stream_trades(symbol):
        swings = detect_swing_points(candle.highs, candle.lows)
        fvgs = detect_fvg(candle.highs, candle.lows, candle.closes)
        score = model.predict(candle.features)
        if score > 0.75:
            print(f"[SIGNAL] {symbol} liquidity_score={score:.2f} swings={len(swings)} fvgs={len(fvgs)}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
