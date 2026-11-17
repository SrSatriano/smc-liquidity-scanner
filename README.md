# SMC Liquidity Scanner

[![CI](https://github.com/SrSatriano/smc-liquidity-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/SrSatriano/smc-liquidity-scanner/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![licença](https://img.shields.io/badge/licen%C3%A7a-MIT-22c55e)

Lê velas OHLC (de um CSV ou da API pública da Bybit) e marca os conceitos de *Smart Money*:
- estrutura de mercado (**BOS** e **CHoCH**);
- **fair value gaps**, acompanhando quando são mitigados e preenchidos;
- **order blocks**;
- **pools de liquidez** (topos e fundos iguais) e as varreduras;
- a zona de **premium/discount**.

O resultado sai como resumo no terminal, em JSON ou num gráfico HTML.

## Uso

```bash
pip install -e .
smcscan scan --csv examples/sintetico_1h.csv --html grafico.html
smcscan scan --bybit BTCUSDT --interval 60 --limit 500     # API pública, sem chave
smcscan scan --csv velas.csv --json > relatorio.json
```

```
examples/sintetico_1h.csv: 240 velas · último fechamento 31463.55 · tendência bullish
range 31241.46 – 31591.94 · equilíbrio 31416.7000 · preço em premium
  BOS   bullish nível 29889.63 em 2026-11-10 00:00
  BOS   bullish nível 31476.01 em 2026-11-10 20:00
  FVG bullish 30954.88 – 31255.2 (aberto desde 2026-11-10 18:00)
  OB  bullish 30659.4 – 31178.05 (não mitigado)
  liquidez equal_lows em 29492.57 (2 toques)
{"fvgs": 54, "fvg_fill_rate": 0.796, "fvg_median_bars_to_fill": 3, "bos": 11, "choch": 7, ...}
```

O exemplo usa velas sintéticas, um passeio aleatório gerado com seed fixa. Abra `examples/sintetico_1h.html` no navegador para ver o gráfico.

Parâmetros:
- `--swing N`: quantas velas de cada lado confirmam um swing (padrão 2).
- `--eq-tolerance`: tolerância relativa para considerar topos e fundos iguais (padrão 0,001).

Como biblioteca:

```python
from smcscan import Candle, analyze, stats
rep = analyze(candles)            # list[Candle]
rep.trend, rep.breaks[-1], rep.zone(candles[-1].close)
```

## Definições

As regras exatas de cada conceito estão em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Cada uma tem um teste com velas montadas à mão.

## Testes

São 9 testes:
- swings, e a garantia de que um swing não é usado antes de confirmado;
- BOS seguido de CHoCH;
- FVG com mitigação e preenchimento;
- order block;
- topos iguais com varredura;
- zonas;
- parser da Bybit, com a API simulada;
- CLI com JSON e HTML.

O CI roda em Linux e Windows.

## Aviso

Ferramenta de análise técnica. Não é recomendação de investimento, e as estatísticas descrevem o passado.

## Autor

Matheus Rodrigues Satriano — [github.com/SrSatriano](https://github.com/SrSatriano)
