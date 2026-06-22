from abc import ABC, abstractmethod
from typing import Union

class BaseFormatter(ABC):
    @abstractmethod
    def format(self, item) -> Union[str, dict]:
        """
        Formats the given item into a string representation for publishing,
        or a dictionary mapping argument names to values (e.g. {'content': text, 'photo': url}).
        """
        pass
