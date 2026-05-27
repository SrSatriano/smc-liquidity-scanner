"""Configuração via variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    symbol: str
    ws_url: str
    use_mock_ws: bool
    model_path: str
    signal_threshold: float
    log_level: str


def load_settings() -> Settings:
    return Settings(
        symbol=os.getenv("SYMBOL", "BTCUSDT"),
        ws_url=os.getenv(
            "BYBIT_WS_URL",
            "wss://stream.bybit.com/v5/public/linear",
        ),
        use_mock_ws=os.getenv("USE_MOCK_WS", "0").strip() in ("1", "true", "yes"),
        model_path=os.getenv("MODEL_PATH", "models/best.pt"),
        signal_threshold=float(os.getenv("SIGNAL_THRESHOLD", "0.75")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
