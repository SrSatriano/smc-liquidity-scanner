<div align="center">

# SMC Liquidity Scanner

**Scanner de liquidez SMC (Smart Money Concepts)**

<p>
  <a href="https://github.com/SrSatriano/smc-liquidity-scanner"><img src="https://img.shields.io/badge/GitHub-smc-liquidity-scanner-24292e?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
</p>

<p>
  <img src="https://img.shields.io/badge/versão-1.0.0-0ea5e9?style=flat-square" alt="versão" />
  <img src="https://img.shields.io/badge/licença-MIT-22c55e?style=flat-square" alt="licença" />
  <img src="https://img.shields.io/badge/idioma-pt--BR-blue?style=flat-square" alt="idioma" />
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-8b5cf6?style=flat-square" alt="ci" />
</p>

<p><strong>Detecção de liquidez institucional, FVG e BOS/CHOCH com machine learning em tempo real.</strong></p>

<p>
  Autor: <a href="https://github.com/SrSatriano">@SrSatriano</a> ·
  Release <strong>1.0.0</strong> (2026-03-26)
</p>

</div>

---

## Índice

1. [Visão geral](#visão-geral)
2. [Problema e solução](#problema-e-solução)
3. [Para quem é](#para-quem-é)
4. [Casos de uso](#casos-de-uso)
5. [Funcionalidades](#funcionalidades)
6. [Stack tecnológica](#stack-tecnológica)
7. [Arquitetura](#arquitetura)
8. [Estrutura do repositório](#estrutura-do-repositório)
9. [Pré-requisitos](#pré-requisitos)
10. [Instalação e execução](#instalação-e-execução)
11. [Configuração](#configuração)
12. [Testes](#testes)
13. [Performance](#performance)
14. [Deploy e operação](#deploy-e-operação)
15. [Limitações conhecidas](#limitações-conhecidas)
16. [Roadmap](#roadmap)
17. [Documentação complementar](#documentação-complementar)
18. [Segurança e licença](#segurança-e-licença)

---

## Visão geral

Este repositório faz parte do **portfólio de engenharia** mantido por [@SrSatriano](https://github.com/SrSatriano). A versão **1.0.0** entrega implementação do núcleo do produto, testes automatizados, pipeline de integração contínua e documentação operacional em **português brasileiro**.

O objetivo é permitir que você clone, execute e evolua o projeto com clareza — do desenvolvimento local ao deploy em produção.

## Problema e solução

| | |
|---|---|
| **Problema** | Operadores manuais perdem zonas de liquidez e desequilíbrios estruturais em múltiplos timeframes. |
| **Solução** | Pipeline que ingere candles via WebSocket, calcula features SMC e classifica setups com modelo treinável. |

## Para quem é

Traders de price action, desks quant e analistas de cripto/ações.

## Casos de uso

- Alertas de order block
- Dashboard de FVG abertos
- Walk-forward de modelo LSTM

## Funcionalidades

- [x] Feed WebSocket Bybit/B3 com reconexão automática
- [x] Features SMC: swings, order blocks, fair value gaps
- [x] Modelo LSTM com exportação ONNX para inferência
- [x] Persistência TimescaleDB e dashboard Grafana
- [x] Docker Compose para stack completa

## Stack tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Principal** | Python, PyTorch, Pandas-TA, WebSockets, TimescaleDB, Grafana |

## Arquitetura

```mermaid
flowchart TB
  WS[Feed WebSocket] --> FE[Features / indicadores]
  FE --> ML[Modelo / ONNX]
  ML --> DB[(TimescaleDB)]
  DB --> GF[Grafana / alertas]
```

Detalhamento de componentes, fluxos de dados e decisões de design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Estrutura do repositório

| Caminho | Descrição |
|---------|-----------|
| `src/scanner/` | Loop principal e ingestão |
| `src/features/` | Indicadores e SMC |
| `docker/` | Compose Timescale + Grafana |

## Pré-requisitos

Python 3.11+, Docker (opcional), conta de API na exchange para feed ao vivo.

## Instalação e execução

```bash
git clone https://github.com/SrSatriano/smc-liquidity-scanner.git
cd smc-liquidity-scanner
```

```bash
docker compose up -d
pip install -r requirements.txt
python -m src.scanner.main
```

## Configuração

| Variável | Descrição | Exemplo |
|----------|-----------|--------|
| `DATABASE_URL` | URL Timescale/Postgres | `postgres://user:pass@localhost:5432/smc` |
| `BYBIT_WS_URL` | Endpoint WebSocket | `wss://stream.bybit.com/v5/public/linear` |

> **Importante:** nunca faça commit de arquivos `.env` com segredos reais. Use `.env.example` como referência.

## Testes

Execute a suíte de testes antes de abrir pull requests:

```bash
pytest tests/ -q
```

A pipeline [`.github/workflows/ci.yml`](.github/workflows/ci.yml) repete build e testes em cada push para `main`.

## Performance

| Métrica | Valor |
|---------|-------|
| Latência sinal→DB | < 80 ms |
| F1 walk-forward | 71% |

Metodologia, hardware de referência e flags de compilação: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Deploy e operação

| Guia | Conteúdo |
|------|----------|
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Homologação, produção e rollback |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Monitoramento, alertas e incidentes |

## Limitações conhecidas

- Modelo padrão é ilustrativo; retreine com seus dados

## Roadmap

- ONNX runtime em C++ para latência sub-10 ms

## Documentação complementar

| Documento | Descrição |
|-----------|-----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura e decisões técnicas |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploy passo a passo |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Runbook operacional |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |
| [SECURITY.md](SECURITY.md) | Política de segurança |
| [AUTHORS.md](AUTHORS.md) | Créditos |

## Segurança e licença

- Dependências revisadas na release **1.0.0**
- Vulnerabilidades: siga [SECURITY.md](SECURITY.md)
- Licença: [MIT](LICENSE) © SrSatriano 2026

---

<p align="center">Desenvolvido com foco em clareza e engenharia de produção · <a href="https://github.com/SrSatriano/smc-liquidity-scanner">Ver no GitHub</a></p>
