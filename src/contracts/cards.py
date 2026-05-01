from abc import ABC, abstractmethod
from typing import Pattern, Any


class IHasRecognitionMask(ABC):
    @abstractmethod
    def get_mask(self) -> Pattern:
        pass


class IHasRecognizedData(ABC):
    @abstractmethod
    def get_data(self) -> Any:
        pass


class ICard(IHasRecognitionMask, IHasRecognizedData):
    pass