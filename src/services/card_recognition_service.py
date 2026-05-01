import easyocr

from cards.completed_order_card import CompletedOrderCard
from cards.order_list_card import OrderListCard
from contracts.cards import IHasRecognizedData

_CARDS = frozenset((
    OrderListCard,
    CompletedOrderCard,
))

class CardRecognitionService:

    def __init__(self):
        self._reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)

    def recognite(self, image_path: str) -> str:
        pass

    def recognite_card(self, image_path: str) -> IHasRecognizedData:
        pass