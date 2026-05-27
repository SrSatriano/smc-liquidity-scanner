#!/usr/bin/env python3
"""Treino mínimo para gerar models/best.pt (demo / CI)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import torch
from torch import nn

from src.models.net import LiquidityNet


def main() -> None:
  out = Path("models/best.pt")
  out.parent.mkdir(parents=True, exist_ok=True)

  model = LiquidityNet()
  opt = torch.optim.Adam(model.parameters(), lr=1e-2)
  loss_fn = nn.BCELoss()

  for _ in range(50):
    x = torch.rand(32, 8)
    y = torch.rand(32, 1)
    pred = model(x)
    loss = loss_fn(pred, y)
    opt.zero_grad()
    loss.backward()
    opt.step()

  torch.save(model.state_dict(), out)
  print(f"Checkpoint salvo em {out}")


if __name__ == "__main__":
  main()
