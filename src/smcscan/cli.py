"""smcscan — scanner de Smart Money Concepts.

smcscan scan --csv velas.csv [--html grafico.html] [--json]
smcscan scan --bybit BTCUSDT --interval 15 [--limit 500]
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

from .analysis import analyze, stats
from .chart import render_html
from .data import fetch_bybit, load_csv


def _fmt_ts(ts: int) -> str:
    if ts < 10**11:  # índice ou segundos pequenos
        return str(ts)
    return datetime.fromtimestamp(ts / 1000, tz=UTC).strftime("%Y-%m-%d %H:%M")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="smcscan")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    src = s.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv")
    src.add_argument("--bybit", metavar="SYMBOL")
    s.add_argument("--interval", default="15")
    s.add_argument("--limit", type=int, default=500)
    s.add_argument("--swing", type=int, default=2, help="velas de cada lado para confirmar um swing")
    s.add_argument("--eq-tolerance", type=float, default=0.001, help="tolerância relativa para topos/fundos iguais")
    s.add_argument("--html", help="grava um gráfico HTML")
    s.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        candles = load_csv(args.csv) if args.csv else fetch_bybit(args.bybit, args.interval, args.limit)
    except (OSError, httpx.HTTPError, RuntimeError, ValueError) as exc:
        print(f"erro ao carregar velas: {exc}")
        return 1
    if len(candles) < 10:
        print("poucas velas para analisar (mínimo 10)")
        return 1
    title = args.csv or f"{args.bybit} {args.interval}"
    rep = analyze(candles, args.swing, args.swing, args.eq_tolerance)
    st = stats(rep, len(candles))
    if args.html:
        Path(args.html).write_text(render_html(candles, rep, title), encoding="utf-8")
    if args.json:
        print(json.dumps({"report": rep.to_dict(), "stats": st}, ensure_ascii=False, indent=2))
        return 0

    last = candles[-1]
    print(f"{title}: {len(candles)} velas · último fechamento {last.close} · tendência {rep.trend}")
    if rep.equilibrium is not None:
        print(f"range {rep.range_low} – {rep.range_high} · equilíbrio {rep.equilibrium:.4f} · preço em {rep.zone(last.close)}")
    for b in rep.breaks[-5:]:
        print(f"  {b.kind:5} {b.direction:7} nível {b.level} em {_fmt_ts(candles[b.index].ts)}")
    open_fvg = [g for g in rep.fvgs if g.filled_at is None][-5:]
    for g in open_fvg:
        print(f"  FVG {g.direction:7} {g.bottom} – {g.top} (aberto desde {_fmt_ts(candles[g.index].ts)})")
    for ob in [o for o in rep.order_blocks if o.mitigated_at is None][-5:]:
        print(f"  OB  {ob.direction:7} {ob.bottom} – {ob.top} (não mitigado)")
    for pool in [x for x in rep.pools if x.swept_at is None][-5:]:
        print(f"  liquidez {pool.kind} em {pool.price} ({len(pool.indices)} toques)")
    print(json.dumps(st, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
