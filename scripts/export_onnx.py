#!/usr/bin/env python3
"""Exporta LiquidityNet para ONNX (models/best.onnx)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import torch

from src.models.net import LiquidityNet


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--checkpoint", default="models/best.pt")
  parser.add_argument("--output", default="models/best.onnx")
  args = parser.parse_args()

  ckpt = Path(args.checkpoint)
  out = Path(args.output)
  out.parent.mkdir(parents=True, exist_ok=True)

  model = LiquidityNet()
  if ckpt.is_file():
    try:
      state = torch.load(ckpt, map_location="cpu", weights_only=True)
    except TypeError:
      state = torch.load(ckpt, map_location="cpu")
    model.load_state_dict(state)
  model.eval()

  dummy = torch.randn(1, 8)
  kwargs: dict = {
    "input_names": ["features"],
    "output_names": ["score"],
    "dynamic_axes": {"features": {0: "batch"}, "score": {0: "batch"}},
    "opset_version": 17,
  }
  try:
    torch.onnx.export(model, dummy, str(out), dynamo=False, **kwargs)
  except TypeError:
    torch.onnx.export(model, dummy, str(out), **kwargs)
  print(f"ONNX salvo em {out}")


if __name__ == "__main__":
  main()
