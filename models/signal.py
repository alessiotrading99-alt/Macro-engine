from dataclasses import dataclass
from datetime import datetime

from .trend import Trend


@dataclass
class TradeSignal:
    direction: Trend     # BULLISH = long, BEARISH = short
    entry: float
    stop_loss: float
    take_profit: float
    fvg_top: float
    fvg_bottom: float
    timestamp: datetime  # timestamp FVG che ha generato il segnale

    @property
    def risk_pips(self) -> float:
        if self.direction == Trend.BULLISH:
            return self.entry - self.stop_loss
        return self.stop_loss - self.entry

    @property
    def reward_pips(self) -> float:
        if self.direction == Trend.BULLISH:
            return self.take_profit - self.entry
        return self.entry - self.take_profit
