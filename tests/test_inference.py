"""Testes do motor de inferência."""

from pathlib import Path

import pytest

from src.models.inference import LiquidityModel


def test_heuristic_predict():
  m = LiquidityModel.load("models/missing.pt")
  assert m.mode == "heuristic"
  score = m.predict([1.0, 0.2, 0.3, 0.1, 0.05, 0.5, 1.0, 0.01])
  assert 0.0 <= score <= 1.0


def test_torch_checkpoint(tmp_path: Path):
  torch = pytest.importorskip("torch")
  from src.models.net import LiquidityNet

  ckpt = tmp_path / "best.pt"
  model = LiquidityNet()
  torch.save(model.state_dict(), ckpt)

  m = LiquidityModel.load(str(ckpt))
  assert m.mode == "torch"
  assert m.predict([0.5] * 8) >= 0.0


def test_onnx_runtime(tmp_path: Path):
  torch = pytest.importorskip("torch")
  ort = pytest.importorskip("onnxruntime")
  from src.models.net import LiquidityNet

  ckpt = tmp_path / "best.pt"
  onnx = tmp_path / "best.onnx"
  model = LiquidityNet()
  model.eval()
  torch.save(model.state_dict(), ckpt)
  dummy = torch.randn(1, 8)
  torch.onnx.export(
    model,
    dummy,
    str(onnx),
    input_names=["features"],
    output_names=["score"],
    opset_version=17,
  )

  m = LiquidityModel.load(str(ckpt))
  assert m.mode == "onnx"
  score = m.predict([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
  assert 0.0 <= score <= 1.0
  _ = ort  # uso explícito para lint
