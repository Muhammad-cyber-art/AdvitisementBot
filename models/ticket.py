from dataclasses import dataclass
from datetime import datetime

@dataclass
class Ticket:
    source: str
    from_city: str
    to_city: str
    departure_date: datetime
    arrival_date: datetime
    airline: str
    price: float
    currency: str
    booking_url: str
