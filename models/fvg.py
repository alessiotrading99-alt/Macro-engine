from dataclasses import dataclass
from datetime import datetime


@dataclass
class FairValueGap:
    timestamp: datetime  # timestamp della candela centrale (impulso)
    top: float           # limite superiore del gap
    bottom: float        # limite inferiore del gap
    is_bullish: bool     # True = gap rialzista, False = ribassista

    @property
    def midpoint(self) -> float:
        return (self.top + self.bottom) / 2
