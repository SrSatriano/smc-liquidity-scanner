from src.features.smc import detect_fvg, detect_swing_points


def test_detect_fvg_bullish():
    highs = [100, 101, 102, 103]
    lows = [90, 91, 105, 106]  # gap: low[2] > high[0]
    closes = [95, 96, 104, 107]
    gaps = detect_fvg(highs, lows, closes)
    assert any(g[1] == "bullish" for g in gaps)


def test_swing_high():
    highs = [1, 2, 5, 2, 1]
    lows = [0, 0, 0, 0, 0]
    swings = detect_swing_points(highs, lows, lookback=1)
    assert any(s.kind == "high" for s in swings)
