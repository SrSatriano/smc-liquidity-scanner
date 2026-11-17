# Arquitetura e definições

```
src/smcscan/
  analysis.py  swings, estrutura (BOS/CHoCH), FVG, order blocks, pools de liquidez, estatísticas
  data.py      velas de CSV ou da API pública da Bybit (v5)
  chart.py     gráfico HTML com SVG puro
  cli.py       smcscan scan
```

## Definições usadas (e testadas)

| Conceito | Regra no código |
|---|---|
| **Swing high/low** | Fractal: a máxima (mínima) é estritamente maior (menor) que as `n` velas de cada lado. Só passa a valer depois de confirmado, `n` velas depois. |
| **BOS** | Fechamento além do último swing confirmado, **a favor** da tendência atual (ou a primeira quebra, partindo de neutro). |
| **CHoCH** | Fechamento além do último swing confirmado **contra** a tendência atual, o que inverte a tendência. |
| **FVG** | Padrão de 3 velas em que a mínima da 3ª fica acima da máxima da 1ª (alta), ou o inverso (baixa). *Mitigado* quando o preço volta até o meio do gap; *preenchido* quando atravessa o gap inteiro. |
| **Order block** | A última vela contrária entre o swing rompido e a vela que fez o BOS/CHoCH. É mitigado quando o preço volta à zona dela. |
| **Pool de liquidez** | Dois ou mais topos (fundos) dentro de uma tolerância relativa (padrão 0,1%). *Varrido* quando uma vela passa o nível no pavio e **fecha de volta** do lado de dentro. |
| **Premium/discount** | Acima ou abaixo do meio do range entre o último swing high e o último swing low. |

Cada regra tem um teste com velas construídas à mão em `tests/test_smc.py`.

## Por que não há "modelo de IA"

A versão anterior tinha uma rede neural sem dados de treino, que devolvia um score sem significado. Ela foi removida. As estatísticas (`stats`) descrevem o histórico analisado: taxa de preenchimento de FVG, nº de BOS/CHoCH, pools varridos. Elas **não** preveem preço.
