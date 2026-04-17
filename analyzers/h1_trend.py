"""
H1 Trend Analyzer
=================
Determina il trend di mercato sull'H1 analizzando la struttura
di swing (massimi e minimi relativi).

  Trend RIALZISTA : Higher High (HH) + Higher Low (HL)
  Trend RIBASSISTA: Lower High  (LH) + Lower Low  (LL)
  Trend NEUTRO    : struttura mista o dati insufficienti
"""

from typing import List, Tuple

from models.candle import Candle
from models.trend import Trend, SwingPoint


class H1TrendAnalyzer:
    """Analizza la struttura H1 e restituisce la direzione del trend."""

    def __init__(self, lookback: int = 30):
        self.lookback = lookback

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_trend(self, h1_candles: List[Candle]) -> Trend:
        """Restituisce il trend corrente H1."""
        if len(h1_candles) < 4:
            return Trend.NEUTRAL

        candles = h1_candles[-self.lookback:]
        swing_highs, swing_lows = self._extract_swings(candles)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return self._close_bias(candles)

        return self._classify(swing_highs, swing_lows)

    def get_swing_points(self, h1_candles: List[Candle]) -> List[SwingPoint]:
        """Restituisce tutti i punti di swing (utile per debug/visualizzazione)."""
        candles = h1_candles[-self.lookback:]
        highs, lows = self._extract_swings(candles)
        high_set = set(highs)
        low_set = set(lows)

        points: List[SwingPoint] = []
        for c in candles[1:-1]:
            if c.high in high_set:
                points.append(SwingPoint(c.timestamp, c.high, is_high=True))
            if c.low in low_set:
                points.append(SwingPoint(c.timestamp, c.low, is_high=False))
        return sorted(points, key=lambda p: p.timestamp)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_swings(candles: List[Candle]) -> Tuple[List[float], List[float]]:
        highs, lows = [], []
        for i in range(1, len(candles) - 1):
            if candles[i].high > candles[i - 1].high and candles[i].high > candles[i + 1].high:
                highs.append(candles[i].high)
            if candles[i].low < candles[i - 1].low and candles[i].low < candles[i + 1].low:
                lows.append(candles[i].low)
        return highs, lows

    @staticmethod
    def _classify(swing_highs: List[float], swing_lows: List[float]) -> Trend:
        hh = swing_highs[-1] > swing_highs[-2]
        hl = swing_lows[-1] > swing_lows[-2]
        lh = swing_highs[-1] < swing_highs[-2]
        ll = swing_lows[-1] < swing_lows[-2]

        if hh and hl:
            return Trend.BULLISH
        if lh and ll:
            return Trend.BEARISH
        if hh or hl:
            return Trend.BULLISH
        if lh or ll:
            return Trend.BEARISH
        return Trend.NEUTRAL

    @staticmethod
    def _close_bias(candles: List[Candle]) -> Trend:
        if candles[-1].close > candles[0].close:
            return Trend.BULLISH
        if candles[-1].close < candles[0].close:
            return Trend.BEARISH
        return Trend.NEUTRAL
