"""Gráfico HTML autocontido (SVG puro, sem bibliotecas) com velas e zonas SMC."""

from __future__ import annotations

import html

from .analysis import Candle, Report


def render_html(candles: list[Candle], rep: Report, title: str = "SMC") -> str:
    w, h, pad = 1200, 560, 50
    n = len(candles)
    lo = min(c.low for c in candles)
    hi = max(c.high for c in candles)
    span = (hi - lo) or 1.0
    cw = (w - 2 * pad) / max(n, 1)

    def x(i: float) -> float:
        return pad + i * cw + cw / 2

    def y(p: float) -> float:
        return pad + (hi - p) / span * (h - 2 * pad)

    parts: list[str] = []

    def rect(i0: int, i1: int, top: float, bot: float, color: str, op: float) -> None:
        parts.append(
            f'<rect x="{x(i0) - cw / 2:.1f}" y="{y(top):.1f}" width="{(i1 - i0 + 1) * cw:.1f}" '
            f'height="{max(y(bot) - y(top), 1):.1f}" fill="{color}" opacity="{op}"/>'
        )

    for g in rep.fvgs:
        end = g.filled_at if g.filled_at is not None else n - 1
        rect(g.index, end, g.top, g.bottom, "#3b82f6" if g.direction == "bullish" else "#f97316", 0.15)
    for ob in rep.order_blocks:
        end = ob.mitigated_at if ob.mitigated_at is not None else n - 1
        rect(ob.index, end, ob.top, ob.bottom, "#16a34a" if ob.direction == "bullish" else "#dc2626", 0.22)
    for p in rep.pools:
        end = p.swept_at if p.swept_at is not None else n - 1
        parts.append(
            f'<line x1="{x(min(p.indices)):.1f}" x2="{x(end):.1f}" y1="{y(p.price):.1f}" y2="{y(p.price):.1f}" '
            f'stroke="#a855f7" stroke-dasharray="4 3"/>'
        )
    for i, c in enumerate(candles):
        up = c.close >= c.open
        color = "#16a34a" if up else "#dc2626"
        parts.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{y(c.high):.1f}" y2="{y(c.low):.1f}" stroke="{color}"/>')
        top, bot = (c.close, c.open) if up else (c.open, c.close)
        parts.append(
            f'<rect x="{x(i) - cw * 0.35:.1f}" y="{y(top):.1f}" width="{cw * 0.7:.1f}" '
            f'height="{max(y(bot) - y(top), 1):.1f}" fill="{color}"/>'
        )
    for b in rep.breaks:
        parts.append(
            f'<line x1="{x(b.swing_index):.1f}" x2="{x(b.index):.1f}" '
            f'y1="{y(b.level):.1f}" y2="{y(b.level):.1f}" stroke="#111827"/>'
            f'<text x="{(x(b.swing_index) + x(b.index)) / 2:.1f}" y="{y(b.level) - 4:.1f}" font-size="10" '
            f'text-anchor="middle">{b.kind}</text>'
        )
    legend = (
        "FVG alta/baixa em azul/laranja · order blocks em verde/vermelho · "
        "liquidez (topos/fundos iguais) tracejada em roxo · linhas pretas: BOS/CHoCH"
    )
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;color:#111827}}svg{{background:#fff;border:1px solid #e5e7eb}}</style>
</head><body><h2>{html.escape(title)}</h2><p>Tendência: <b>{rep.trend}</b> · {html.escape(legend)}</p>
<svg viewBox="0 0 {w} {h}" width="100%">{"".join(parts)}</svg></body></html>"""
