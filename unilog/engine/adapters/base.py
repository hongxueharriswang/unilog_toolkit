
from abc import ABC, abstractmethod
from .env import NotAvailable

class ExternalAdapter(ABC):
    @abstractmethod
    def is_available(self) -> bool: ...
