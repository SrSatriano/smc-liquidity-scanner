"""Smart Money Concepts sobre velas OHLC.

Tudo aqui é determinístico e testável: swings por fractal, estrutura de mercado
(BOS e CHoCH), fair value gaps com acompanhamento de mitigação, order blocks,
pools de liquidez (topos/fundos iguais) e varreduras (sweeps).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Candle:
    ts: int  # epoch em ms
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class Swing:
    index: int
    price: float
    kind: str  # "high" | "low"


@dataclass
class StructureBreak:
    index: int  # vela que fechou além do nível
    kind: str  # "BOS" (continuação) | "CHoCH" (mudança de caráter)
    direction: str  # "bullish" | "bearish"
    level: float
    swing_index: int


@dataclass
class FVG:
    index: int  # vela do meio do padrão de 3 velas
    direction: str
    top: float
    bottom: float
    mitigated_at: int | None = None  # vela que preencheu 50% do gap
    filled_at: int | None = None  # vela que fechou o gap inteiro


@dataclass
class OrderBlock:
    index: int
    direction: str
    top: float
    bottom: float
    origin_break: int  # índice do BOS/CHoCH que validou o bloco
    mitigated_at: int | None = None


@dataclass
class LiquidityPool:
    kind: str  # "equal_highs" | "equal_lows"
    price: float
    indices: list[int]
    swept_at: int | None = None


@dataclass
class Report:
    swings: list[Swing] = field(default_factory=list)
    breaks: list[StructureBreak] = field(default_factory=list)
    fvgs: list[FVG] = field(default_factory=list)
    order_blocks: list[OrderBlock] = field(default_factory=list)
    pools: list[LiquidityPool] = field(default_factory=list)
    trend: str = "neutral"
    range_high: float | None = None
    range_low: float | None = None

    @property
    def equilibrium(self) -> float | None:
        if self.range_high is None or self.range_low is None:
            return None
        return (self.range_high + self.range_low) / 2

    def zone(self, price: float) -> str | None:
        """Premium (acima do equilíbrio) ou discount (abaixo) no range atual."""
        eq = self.equilibrium
        if eq is None:
            return None
        return "premium" if price > eq else "discount"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["equilibrium"] = self.equilibrium
        return d


def swings(candles: list[Candle], left: int = 2, right: int = 2) -> list[Swing]:
    """Fractal: máxima maior que as `left` anteriores e as `right` seguintes."""
    out: list[Swing] = []
    for i in range(left, len(candles) - right):
        h, lo = candles[i].high, candles[i].low
        window = candles[i - left : i] + candles[i + 1 : i + 1 + right]
        if all(h > c.high for c in window):
            out.append(Swing(i, h, "high"))
        if all(lo < c.low for c in window):
            out.append(Swing(i, lo, "low"))
    return out


def structure(candles: list[Candle], sw: list[Swing], right: int = 2) -> tuple[list[StructureBreak], str]:
    """Percorre as velas e marca quando o fechamento rompe o último swing confirmado.

    Um swing só pode ser usado depois de confirmado (`right` velas depois dele).
    Rompimento a favor da tendência = BOS; contra = CHoCH.
    """
    breaks: list[StructureBreak] = []
    trend = "neutral"
    last_high: Swing | None = None
    last_low: Swing | None = None
    used: set[int] = set()
    by_confirm: dict[int, list[Swing]] = {}
    for s in sw:
        by_confirm.setdefault(s.index + right, []).append(s)

    for i, c in enumerate(candles):
        for s in by_confirm.get(i, []):
            if s.kind == "high":
                last_high = s
            else:
                last_low = s
        if last_high and last_high.index not in used and c.close > last_high.price:
            kind = "BOS" if trend == "bullish" else ("CHoCH" if trend == "bearish" else "BOS")
            breaks.append(StructureBreak(i, kind, "bullish", last_high.price, last_high.index))
            used.add(last_high.index)
            trend = "bullish"
        if last_low and last_low.index not in used and c.close < last_low.price:
            kind = "BOS" if trend == "bearish" else ("CHoCH" if trend == "bullish" else "BOS")
            breaks.append(StructureBreak(i, kind, "bearish", last_low.price, last_low.index))
            used.add(last_low.index)
            trend = "bearish"
    return breaks, trend


def fair_value_gaps(candles: list[Candle], min_size: float = 0.0) -> list[FVG]:
    out: list[FVG] = []
    for i in range(2, len(candles)):
        a, c = candles[i - 2], candles[i]
        if c.low > a.high and c.low - a.high > min_size:
            out.append(FVG(i - 1, "bullish", top=c.low, bottom=a.high))
        elif c.high < a.low and a.low - c.high > min_size:
            out.append(FVG(i - 1, "bearish", top=a.low, bottom=c.high))
    for g in out:
        mid = (g.top + g.bottom) / 2
        for j in range(g.index + 2, len(candles)):
            k = candles[j]
            if g.direction == "bullish":
                if g.mitigated_at is None and k.low <= mid:
                    g.mitigated_at = j
                if k.low <= g.bottom:
                    g.filled_at = j
                    break
            else:
                if g.mitigated_at is None and k.high >= mid:
                    g.mitigated_at = j
                if k.high >= g.top:
                    g.filled_at = j
                    break
    return out


def order_blocks(candles: list[Candle], breaks: list[StructureBreak]) -> list[OrderBlock]:
    """Última vela contrária antes do impulso que causou o rompimento."""
    out: list[OrderBlock] = []
    for b in breaks:
        start = b.swing_index
        rng = range(b.index - 1, start - 1, -1)
        for j in rng:
            k = candles[j]
            opposite = k.close < k.open if b.direction == "bullish" else k.close > k.open
            if opposite:
                ob = OrderBlock(j, b.direction, top=k.high, bottom=k.low, origin_break=b.index)
                for m in range(b.index + 1, len(candles)):
                    x = candles[m]
                    if (b.direction == "bullish" and x.low <= ob.top) or (b.direction == "bearish" and x.high >= ob.bottom):
                        ob.mitigated_at = m
                        break
                out.append(ob)
                break
    return out


def liquidity_pools(candles: list[Candle], sw: list[Swing], tolerance: float = 0.001) -> list[LiquidityPool]:
    """Topos/fundos iguais (dentro de `tolerance` relativa) e a vela que os varreu:
    pavio além do nível com fechamento de volta para dentro."""
    pools: list[LiquidityPool] = []
    for kind, label in (("high", "equal_highs"), ("low", "equal_lows")):
        pts = [s for s in sw if s.kind == kind]
        groups: list[list[Swing]] = []
        for s in pts:
            for g in groups:
                if abs(s.price - g[0].price) / g[0].price <= tolerance:
                    g.append(s)
                    break
            else:
                groups.append([s])
        for g in groups:
            if len(g) < 2:
                continue
            level = max(x.price for x in g) if kind == "high" else min(x.price for x in g)
            pool = LiquidityPool(label, level, [x.index for x in g])
            for j in range(max(pool.indices) + 1, len(candles)):
                k = candles[j]
                if kind == "high" and k.high > level:
                    if k.close < level:
                        pool.swept_at = j
                    break
                if kind == "low" and k.low < level:
                    if k.close > level:
                        pool.swept_at = j
                    break
            pools.append(pool)
    return pools


def analyze(candles: list[Candle], left: int = 2, right: int = 2, eq_tolerance: float = 0.001) -> Report:
    if len(candles) < left + right + 3:
        return Report()
    sw = swings(candles, left, right)
    br, trend = structure(candles, sw, right)
    rep = Report(
        swings=sw,
        breaks=br,
        fvgs=fair_value_gaps(candles),
        order_blocks=order_blocks(candles, br),
        pools=liquidity_pools(candles, sw, eq_tolerance),
        trend=trend,
    )
    highs = [s.price for s in sw if s.kind == "high"]
    lows = [s.price for s in sw if s.kind == "low"]
    if highs and lows:
        rep.range_high, rep.range_low = highs[-1], lows[-1]
        if rep.range_high < rep.range_low:
            rep.range_high, rep.range_low = rep.range_low, rep.range_high
    return rep


def stats(rep: Report, n_candles: int) -> dict:
    """Estatísticas descritivas do histórico (não são previsão)."""
    closed = [g for g in rep.fvgs if g.index < n_candles - 2]
    filled = [g for g in closed if g.filled_at is not None]
    lag = [g.filled_at - g.index for g in filled]
    swept = [p for p in rep.pools if p.swept_at is not None]
    return {
        "fvgs": len(rep.fvgs),
        "fvg_fill_rate": round(len(filled) / len(closed), 3) if closed else None,
        "fvg_median_bars_to_fill": sorted(lag)[len(lag) // 2] if lag else None,
        "bos": sum(1 for b in rep.breaks if b.kind == "BOS"),
        "choch": sum(1 for b in rep.breaks if b.kind == "CHoCH"),
        "order_blocks": len(rep.order_blocks),
        "order_blocks_unmitigated": sum(1 for o in rep.order_blocks if o.mitigated_at is None),
        "liquidity_pools": len(rep.pools),
        "pools_swept": len(swept),
    }
