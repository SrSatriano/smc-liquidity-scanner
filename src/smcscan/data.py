"""Fontes de velas: CSV local ou API pública da Bybit (v5, sem chave)."""

from __future__ import annotations

import csv
from pathlib import Path

import httpx

from .analysis import Candle

BYBIT_REST = "https://api.bybit.com/v5/market/kline"
INTERVALS = {"1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"}


def load_csv(path: str | Path) -> list[Candle]:
    """CSV com cabeçalho contendo ts (ou time/timestamp), open, high, low, close[, volume]."""
    out: list[Candle] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = {c.lower(): c for c in reader.fieldnames or []}
        ts_col = next((cols[c] for c in ("ts", "time", "timestamp", "date") if c in cols), None)
        for i, row in enumerate(reader):
            out.append(
                Candle(
                    ts=int(float(row[ts_col])) if ts_col else i,
                    open=float(row[cols["open"]]),
                    high=float(row[cols["high"]]),
                    low=float(row[cols["low"]]),
                    close=float(row[cols["close"]]),
                    volume=float(row[cols["volume"]]) if "volume" in cols else 0.0,
                )
            )
    out.sort(key=lambda c: c.ts)
    return out


def fetch_bybit(
    symbol: str, interval: str = "15", limit: int = 500, category: str = "linear", client: httpx.Client | None = None
) -> list[Candle]:
    if interval not in INTERVALS:
        raise ValueError(f"intervalo inválido: {interval}")
    client = client or httpx.Client(timeout=15)
    r = client.get(
        BYBIT_REST, params={"category": category, "symbol": symbol.upper(), "interval": interval, "limit": min(limit, 1000)}
    )
    r.raise_for_status()
    body = r.json()
    if body.get("retCode") != 0:
        raise RuntimeError(f"Bybit: {body.get('retMsg')}")
    # A Bybit devolve do mais novo para o mais antigo: [start, open, high, low, close, volume, turnover]
    rows = body["result"]["list"]
    return sorted(
        (Candle(int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])) for x in rows),
        key=lambda c: c.ts,
    )
