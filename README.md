# SMC Liquidity Scanner

Bot analítico que consome dados via WebSocket (B3 ou Bybit), processa Order Flow em tempo real e identifica zonas de liquidez institucionais e quebras de estrutura (BOS/CHOCH) com redes neurais.

## Stack

- Python 3.11+
- PyTorch / TensorFlow
- Pandas-TA, NumPy
- WebSockets, asyncio
- TimescaleDB + Grafana (dashboard)

## Matemática da detecção de liquidez

### Order Blocks e Fair Value Gaps (FVG)

- **FVG bullish**: `low[i] > high[i-2]` — gap de 3 velas.
- **Order Block**: última vela contrária antes de um deslocamento > `k × ATR(14)`.

### BOS / CHOCH

- **BOS (Break of Structure)**: fechamento além do último swing high/low confirmado.
- **CHOCH (Change of Character)**: primeiro BOS contra a tendência dominante no timeframe superior.

### Score de liquidez institucional

```
L_score = w1·(volume_cluster) + w2·(delta_imbalance) + w3·(NN_confidence)
```

Onde `delta_imbalance` é a razão entre agressões compradoras e vendedoras no cluster de preço.

Documentação: [docs/LIQUIDITY_MATH.md](docs/LIQUIDITY_MATH.md) | [docs/MODEL_TRAINING.md](docs/MODEL_TRAINING.md)

## Treinamento da rede neural

- **Entrada**: janela de 64 features (OHLCV, delta, book imbalance, distância a swings).
- **Arquitetura**: LSTM (2 camadas, 128 unidades) + cabeça softmax (3 classes: acumulação, distribuição, neutro).
- **Loss**: focal loss para classes desbalanceadas.
- **Validação**: walk-forward por semana; sem shuffle temporal.

## Docker Compose

```bash
docker compose up -d
```

Serviços: TimescaleDB, Grafana, scanner (ver `docker-compose.yml`).

| Serviço | Porta |
|---------|-------|
| TimescaleDB | 5432 |
| Grafana | 3000 |
| Scanner API | 8080 |

## Configuração

```bash
cp config/example.env .env
pip install -r requirements.txt
python -m src.scanner.main --exchange bybit --symbol BTCUSDT
```

## Estrutura

| Pasta | Função |
|-------|--------|
| `src/scanner/` | Loop principal e sinais |
| `src/models/` | Checkpoints e inferência |
| `src/websocket/` | Feeds B3/Bybit |
| `dashboard/` | Queries Grafana |

## Aviso

Ferramenta de análise educacional. Não constitui recomendação de investimento.
