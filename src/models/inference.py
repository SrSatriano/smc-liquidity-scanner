"""Inferência PyTorch ou ONNX Runtime."""

from __future__ import annotations

from pathlib import Path

import numpy as np

FEATURE_DIM = 8


class LiquidityModel:
  def __init__(self, mode: str = "heuristic") -> None:
    self.mode = mode
    self._torch_model = None
    self._onnx_session = None

  @classmethod
  def load(cls, path: str) -> "LiquidityModel":
    base = Path(path)
    onnx_path = base.with_suffix(".onnx")
    if not onnx_path.name.endswith(".onnx"):
      onnx_path = Path(str(base).replace(".pt", ".onnx"))

    if onnx_path.is_file():
      try:
        import onnxruntime as ort

        session = ort.InferenceSession(
          str(onnx_path),
          providers=["CPUExecutionProvider"],
        )
        m = cls("onnx")
        m._onnx_session = session
        return m
      except ImportError:
        pass

    if base.is_file():
      try:
        import torch

        from src.models.net import LiquidityNet

        model = LiquidityNet(FEATURE_DIM)
        try:
          state = torch.load(base, map_location="cpu", weights_only=True)
        except TypeError:
          state = torch.load(base, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
        m = cls("torch")
        m._torch_model = model
        return m
      except Exception:
        pass

    return cls("heuristic")

  def predict(self, features: list[float]) -> float:
    vec = _pad_features(features)

    if self.mode == "onnx" and self._onnx_session is not None:
      inp = np.array([vec], dtype=np.float32)
      out = self._onnx_session.run(None, {"features": inp})[0]
      return float(out[0][0])

    if self.mode == "torch" and self._torch_model is not None:
      import torch

      t = torch.tensor([vec], dtype=torch.float32)
      with torch.no_grad():
        return float(self._torch_model(t)[0, 0].item())

    return min(1.0, sum(abs(x) for x in vec) / max(len(vec), 1) / 10.0)


def _pad_features(features: list[float], size: int = FEATURE_DIM) -> list[float]:
  if len(features) >= size:
    return features[:size]
  return features + [0.0] * (size - len(features))
