import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import List
from models.ticket import Ticket
from collectors.base import BaseCollector

class AviasalesCollector(BaseCollector):
    def __init__(self, token: str = "0a9fbe3435e7a56e89e2e297b7d9f100"):
        self.token = token
        # Travelpayouts (Aviasales) v2 Prices API for latest prices
        self.api_url = "https://api.aviationstack.com/v1/flights"

    @property
    def source_name(self) -> str:
        return "Aviasales"

    def collect(self, from_city: str, to_city: str, date: str) -> List[Ticket]:
        params = {
            "origin": from_city,
            "destination": to_city,
            "beginning_of_period": date,
            "period_type": "day",
            "limit": 10,
            "show_to_affiliates": "true",
            "sorting": "price",
            "token": self.token
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.api_url}?{query_string}"
        
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        tickets = []
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                if data.get("success") and "data" in data:
                    for item in data["data"]:
                        departure_str = item.get("depart_date", "")
                        dep_date = datetime.strptime(departure_str, "%Y-%m-%d") if departure_str else datetime.now()
                        
                        # Data API usually doesn't return precise arrival for "latest prices" 
                        # We mock it as the same day for PoC
                        arr_date = dep_date 
                        
                        # Generate a mock booking url to aviasales
                        search_date = date.replace("-", "")
                        booking_url = f"https://www.aviasales.uz/search/{from_city}{search_date}{to_city}1"
                        
                        ticket = Ticket(
                            source=self.source_name,
                            from_city=item.get("origin", from_city),
                            to_city=item.get("destination", to_city),
                            departure_date=dep_date,
                            arrival_date=arr_date,
                            airline=item.get("gate", "Unknown"), 
                            price=float(item.get("value", 0.0)),
                            currency="RUB", # Default currency in this endpoint
                            booking_url=booking_url
                        )
                        tickets.append(ticket)
        except urllib.error.HTTPError as e:
            print(f"[{self.source_name}] API HTTP Xatosi: {e.code} - {e.reason}")
            print("Izoh: Agar Aviasales (Travelpayouts) API tokeningiz yaroqsiz bo'lsa (401), iltimos travelpayouts.com dan yangi token oling.")
        except Exception as e:
            print(f"[{self.source_name}] Xatolik yuz berdi: {e}")
            
        return tickets
