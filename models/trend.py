from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Trend(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class SwingPoint:
    timestamp: datetime
    price: float
    is_high: bool  # True = swing high, False = swing low
