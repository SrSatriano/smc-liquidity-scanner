# Treinamento do modelo

## Dataset

1. Exportar ticks/velas do TimescaleDB.
2. Rotular manualmente ou via regras heurísticas (BOS confirmado + reteste).
3. Split temporal: 70% treino, 15% val, 15% teste.

## Hiperparâmetros sugeridos

| Parâmetro | Valor |
|-----------|-------|
| batch_size | 64 |
| lr | 1e-4 |
| epochs | 50 |
| early_stopping | patience=7 |

## Export

```bash
python scripts/export_onnx.py --checkpoint models/best.pt
```

Inferência em tempo real usa ONNX Runtime para menor latência.
