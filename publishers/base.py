from abc import ABC, abstractmethod

class BasePublisher(ABC):
    @abstractmethod
    async def publish(self, content: str, photo: str = None) -> bool:
        """
        Publishes the content asynchronously.
        Optionally attaches a photo if the publisher supports it.
        Returns True if successful, False otherwise.
        """
        pass
