from abc import ABC, abstractmethod
from typing import List
from models.ticket import Ticket

class BaseCollector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Returns the name of the source platform."""
        pass

    @abstractmethod
    def collect(self, from_city: str, to_city: str, date: str) -> List[Ticket]:
        """
        Gathers tickets for a specific route and date.
        
        Args:
            from_city (str): IATA code of origin city
            to_city (str): IATA code of destination city
            date (str): Departure date in YYYY-MM-DD format
            
        Returns:
            List[Ticket]: List of collected tickets
        """
        pass
