import json

import httpx
import pytest

from smcscan.analysis import Candle, analyze, fair_value_gaps, liquidity_pools, order_blocks, stats, structure, swings
from smcscan.cli import main
from smcscan.data import fetch_bybit, load_csv


def series(mids: list[float], wick: float = 1.0) -> list[Candle]:
    """Velas com máxima/mínima a `wick` do fechamento e abertura no fechamento anterior (limitada ao range)."""
    out, prev = [], mids[0]
    for i, m in enumerate(mids):
        hi, lo = m + wick, m - wick
        out.append(Candle(i, min(max(prev, lo), hi), hi, lo, m))
        prev = m
    return out


# zigue-zague: sobe até 110, corrige até 100, rompe 110 (BOS de alta), faz novo topo,
# corrige, e depois perde o fundo anterior (CHoCH de baixa).
ZIGZAG = [100, 103, 106, 110, 107, 104, 100, 103, 107, 112, 116, 119, 115, 111, 108, 111, 114, 110, 105, 101, 98]


def test_swings_by_fractal():
    sw = swings(series(ZIGZAG))
    highs = [(s.index, s.price) for s in sw if s.kind == "high"]
    lows = [(s.index, s.price) for s in sw if s.kind == "low"]
    assert (3, 111) in highs and (11, 120) in highs
    assert (6, 99) in lows and (14, 107) in lows


def test_bos_then_choch():
    cs = series(ZIGZAG)
    breaks, trend = structure(cs, swings(cs))
    assert breaks[0].kind == "BOS" and breaks[0].direction == "bullish" and breaks[0].level == 111
    assert breaks[0].index == 9  # primeira vela que FECHA acima de 111
    choch = [b for b in breaks if b.kind == "CHoCH"]
    assert choch and choch[0].direction == "bearish" and choch[0].level == 107
    assert trend == "bearish"


def test_swing_is_not_used_before_confirmation():
    # Rompe o topo antes de ele ter as 2 velas da direita: não pode haver BOS ali.
    cs = series([100, 102, 104, 103, 105, 107, 109])
    breaks, _ = structure(cs, swings(cs))
    assert breaks == []


def test_fvg_detection_and_fill():
    cs = [
        Candle(0, 100, 101, 99, 100.5),
        Candle(1, 100.5, 106, 100.4, 105.8),  # impulso
        Candle(2, 105.8, 107, 103, 106.5),  # low 103 > high 101 da vela 0 → FVG de alta 101–103
        Candle(3, 106.5, 107, 101.9, 104),  # atinge o meio (102)
        Candle(4, 104, 104.5, 100.5, 101),  # passa do fundo do gap: preenchido
    ]
    g = fair_value_gaps(cs)[0]
    assert (g.direction, g.bottom, g.top, g.index) == ("bullish", 101, 103, 1)
    assert g.mitigated_at == 3 and g.filled_at == 4


def test_order_block_is_last_opposite_candle_before_break():
    cs = series(ZIGZAG)
    br, _ = structure(cs, swings(cs))
    obs = order_blocks(cs, br)
    bull = next(o for o in obs if o.direction == "bullish")
    c = cs[bull.index]
    assert c.close < c.open  # vela de baixa
    assert bull.index < br[0].index and bull.index >= br[0].swing_index


def test_equal_highs_and_sweep():
    cs = series([100, 104, 108, 104, 100, 104, 108.05, 104, 100, 103, 106])
    # vela de varredura: pavio acima de 109 e fechamento de volta abaixo
    cs.append(Candle(11, 106, 110, 105, 107))
    pools = liquidity_pools(cs, swings(cs), tolerance=0.002)
    eqh = next(p for p in pools if p.kind == "equal_highs")
    assert eqh.indices == [2, 6]
    assert eqh.swept_at == 11


def test_report_zones_and_stats():
    cs = series(ZIGZAG)
    rep = analyze(cs)
    assert rep.range_high is not None and rep.range_low is not None
    assert rep.zone(rep.range_high) == "premium" and rep.zone(rep.range_low) == "discount"
    st = stats(rep, len(cs))
    assert st["bos"] >= 1 and st["choch"] >= 1
    assert analyze(cs[:3]).breaks == []


def test_bybit_fetch_parses_and_sorts():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.params["symbol"] == "BTCUSDT" and req.url.params["interval"] == "15"
        rows = [["2000", "2", "3", "1", "2.5", "10", "0"], ["1000", "1", "2", "0.5", "2", "5", "0"]]
        return httpx.Response(200, json={"retCode": 0, "result": {"list": rows}})

    cs = fetch_bybit("btcusdt", "15", client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert [c.ts for c in cs] == [1000, 2000] and cs[1].close == 2.5
    with pytest.raises(ValueError):
        fetch_bybit("BTCUSDT", "7")
    err = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"retCode": 10001, "retMsg": "x"})))
    with pytest.raises(RuntimeError):
        fetch_bybit("BTCUSDT", client=err)


def test_cli_csv_json_and_html(tmp_path, capsys):
    path = tmp_path / "velas.csv"
    lines = ["timestamp,open,high,low,close,volume"] + [f"{c.ts},{c.open},{c.high},{c.low},{c.close},1" for c in series(ZIGZAG)]
    path.write_text("\n".join(lines))
    assert len(load_csv(path)) == len(ZIGZAG)
    html_out = tmp_path / "g.html"
    assert main(["scan", "--csv", str(path), "--html", str(html_out), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["report"]["trend"] == "bearish" and data["stats"]["choch"] >= 1
    page = html_out.read_text(encoding="utf-8")
    assert page.startswith("<!DOCTYPE html>") and "CHoCH" in page
