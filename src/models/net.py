"""Rede leve para score de liquidez (exportável para ONNX)."""

from __future__ import annotations

import torch
from torch import nn


class LiquidityNet(nn.Module):
  """MLP 8 → 16 → 1 com sigmoid."""

  def __init__(self, in_features: int = 8) -> None:
    super().__init__()
    self.net = nn.Sequential(
      nn.Linear(in_features, 16),
      nn.ReLU(),
      nn.Linear(16, 1),
      nn.Sigmoid(),
    )

  def forward(self, x: torch.Tensor) -> torch.Tensor:
    return self.net(x)
