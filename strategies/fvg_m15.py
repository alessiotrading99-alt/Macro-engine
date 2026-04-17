"""
FVG M15 Strategy
================
Regole operative:
  1. Dopo le 06:00 ora italiana (Europe/Rome) cerca il PRIMO FVG su M15
     che sia allineato con il trend H1.
  2. Il trend H1 determina la direzione:
       BULLISH → cerca FVG rialzista (imbalance verso l'alto)
       BEARISH → cerca FVG ribassista (imbalance verso il basso)
       NEUTRAL → nessuna operazione
  3. Entry: al livello inferiore del FVG (long) o superiore (short)
     — ordine limite che aspetta il ritorno nel gap.
  4. Stop Loss : 20 pips dall'entry.
  5. Take Profit: 30 pips dall'entry (R/R 1 : 1,5).

FVG rialzista  : candle[i-1].high < candle[i+1].low
FVG ribassista : candle[i-1].low  > candle[i+1].high
"""

from datetime import time
from typing import List, Optional

import pytz

from analyzers.h1_trend import H1TrendAnalyzer
from models.candle import Candle
from models.fvg import FairValueGap
from models.signal import TradeSignal
from models.trend import Trend


class FvgM15Strategy:
    """Strategia FVG su M15 con filtro direzionale H1."""

    _ROME_TZ = pytz.timezone("Europe/Rome")
    _SESSION_OPEN = time(6, 0)  # 06:00 ora italiana

    def __init__(
        self,
        pip_size: float = 0.0001,
        stop_pips: int = 20,
        rr_ratio: float = 1.5,
        h1_lookback: int = 30,
    ):
        """
        Parameters
        ----------
        pip_size   : valore di 1 pip (0.0001 per EUR/USD, 0.01 per JPY pairs)
        stop_pips  : distanza dello stop loss in pips
        rr_ratio   : rapporto rischio/rendimento (1.5 → 30 pips di TP con 20 di SL)
        h1_lookback: numero di candele H1 da analizzare per il trend
        """
        self.pip_size = pip_size
        self.stop_pips = stop_pips
        self.rr_ratio = rr_ratio
        self._analyzer = H1TrendAnalyzer(lookback=h1_lookback)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_signal(
        self,
        h1_candles: List[Candle],
        m15_candles: List[Candle],
    ) -> Optional[TradeSignal]:
        """
        Restituisce il primo segnale operativo della sessione oppure None
        se non ci sono condizioni valide.

        Parameters
        ----------
        h1_candles  : candele H1 (almeno 4, idealmente >= 30)
        m15_candles : candele M15 della giornata corrente
        """
        trend = self._analyzer.get_trend(h1_candles)
        if trend == Trend.NEUTRAL:
            return None

        post_open = self._candles_after_session_open(m15_candles)
        if len(post_open) < 3:
            return None

        fvg = self._find_first_fvg(post_open, trend)
        if fvg is None:
            return None

        return self._build_signal(fvg, trend)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _candles_after_session_open(self, candles: List[Candle]) -> List[Candle]:
        """Filtra le candele M15 successive alle 06:00 ora di Roma."""
        result = []
        for c in candles:
            ts = c.timestamp
            if ts.tzinfo is None:
                ts = pytz.utc.localize(ts)
            rome_time = ts.astimezone(self._ROME_TZ).time()
            if rome_time >= self._SESSION_OPEN:
                result.append(c)
        return result

    def _find_first_fvg(
        self,
        candles: List[Candle],
        trend: Trend,
    ) -> Optional[FairValueGap]:
        """Trova il primo FVG allineato al trend nella lista di candele."""
        for i in range(1, len(candles) - 1):
            prev, curr, nxt = candles[i - 1], candles[i], candles[i + 1]

            if trend == Trend.BULLISH and prev.high < nxt.low:
                return FairValueGap(
                    timestamp=curr.timestamp,
                    top=nxt.low,
                    bottom=prev.high,
                    is_bullish=True,
                )

            if trend == Trend.BEARISH and prev.low > nxt.high:
                return FairValueGap(
                    timestamp=curr.timestamp,
                    top=prev.low,
                    bottom=nxt.high,
                    is_bullish=False,
                )

        return None

    def _build_signal(self, fvg: FairValueGap, trend: Trend) -> TradeSignal:
        """Costruisce il TradeSignal con SL e TP calcolati in pips."""
        sl_distance = self.stop_pips * self.pip_size
        tp_distance = self.stop_pips * self.rr_ratio * self.pip_size

        if trend == Trend.BULLISH:
            entry = fvg.bottom          # limite buy al bordo inferiore del gap
            stop_loss = entry - sl_distance
            take_profit = entry + tp_distance
        else:
            entry = fvg.top             # limite sell al bordo superiore del gap
            stop_loss = entry + sl_distance
            take_profit = entry - tp_distance

        return TradeSignal(
            direction=trend,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            fvg_top=fvg.top,
            fvg_bottom=fvg.bottom,
            timestamp=fvg.timestamp,
        )
