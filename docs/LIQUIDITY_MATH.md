# Matemática — Detecção de liquidez SMC

## Swing points

Swing high em `i` se `high[i] > high[i±k]` para `k ∈ [1, lookback]`.

## Volume Profile

Para cada faixa de preço `p`:

```
VP(p) = Σ volume onde price ∈ [p - ε, p + ε]
```

Zonas de liquidez: máximos locais de `VP(p)` acima do percentil 85.

## Integração com NN

Features normalizadas com z-score rolling (janela 500). O modelo refina `L_score` aprendendo padrões não lineares em sequências de delta.
