# Macro Engine — H1 Trend Analyzer

## Descrizione

Modulo di analisi del trend su timeframe **H1** tramite struttura di swing.
Utilizzato come filtro direzionale dalla strategia FVG M15 di `engine-2`.

## Logica Trend H1

| Struttura | Trend |
|---|---|
| Higher High + Higher Low | RIALZISTA |
| Lower High + Lower Low | RIBASSISTA |
| Misto / dati insufficienti | NEUTRO |

## Struttura Progetto

```
macro-engine/
├── analyzers/
│   └── h1_trend.py    # H1TrendAnalyzer
├── models/
│   ├── candle.py      # Candle dataclass
│   └── trend.py       # Trend enum + SwingPoint dataclass
└── requirements.txt
```

## Utilizzo

```python
from analyzers import H1TrendAnalyzer
from models.trend import Trend

analyzer = H1TrendAnalyzer(lookback=30)
trend = analyzer.get_trend(h1_bars)  # List[Candle]

if trend == Trend.BULLISH:
    print("Trend rialzista -> cercare FVG bullish su M15")
elif trend == Trend.BEARISH:
    print("Trend ribassista -> cercare FVG bearish su M15")
```
