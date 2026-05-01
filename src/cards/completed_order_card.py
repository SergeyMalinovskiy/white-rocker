from typing import Pattern, Any

from contracts.cards import IHasRecognitionMask, ICard


class CompletedOrderCard(ICard):
    def __init__(self, data):
        self._data = data

    def get_mask(self) -> Pattern:
        pass

    def get_data(self) -> Any:
        return self._data
