"""Inferência do modelo de liquidez."""

from __future__ import annotations

from pathlib import Path


class LiquidityModel:
    def __init__(self, checkpoint: str | None = None) -> None:
        self.checkpoint = checkpoint
        self._loaded = False

    @classmethod
    def load(cls, path: str) -> "LiquidityModel":
        p = Path(path)
        if not p.exists():
            return cls(None)  # modo heurístico sem pesos
        return cls(str(p))

    def predict(self, features: list[float]) -> float:
        if not self.checkpoint:
            # fallback heurístico
            return min(1.0, sum(abs(x) for x in features[:8]) / max(len(features), 1) / 10)
        # TODO: torch/onnx inference
        return 0.5
