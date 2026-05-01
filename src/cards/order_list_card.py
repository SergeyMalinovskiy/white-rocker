from re import Pattern
from typing import Any

from contracts.cards import IHasRecognitionMask, ICard


class OrderListCard(ICard):
    def __init__(self, data):
        self._data = data

    def get_mask(self) -> Pattern:
        pass

    def get_data(self) -> Any:
        return self._data

