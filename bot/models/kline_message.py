from dataclasses import dataclass
from datetime import datetime

@dataclass
class KlineMessage:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_closed: bool
    symbol: str
    interval: str

    @property
    def time_utc(self) -> datetime:
        """Zwraca czas otwarcia świecy w UTC."""
        return datetime.utcfromtimestamp(self.timestamp / 1000)
    