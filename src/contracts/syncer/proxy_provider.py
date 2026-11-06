from contracts.syncer.result import ISyncMessage

LimitUnit = Union['day', 'hour', 'minute', 'second']
SendLimit = 1
ReadLimit = 2
LimitType = Union[SendLimit, ReadLimit]
ExchangeLimit = Tuple[
    LimitType, # на что ограничение на отправку данных или на чтение
    int, # численное отражение лимита
    LimitUnit, # период ограничения
]

class ICanLetExchangeMessages(ABC):
    @abstractmethod
    def send_message(self, message: ISyncMessage) -> None:
        pass

    @abstractmethod
    def read_messages(self, filters: List[str]) -> List[ISyncMessage]:
        pass


class IHasLimits(ABC):

    """
    Определяем какие лимиты есть у провайдера
    """
    @abstractmethod
    def get_limits(self) -> List[ExchangeLimit]:
        pass

    """
    Сколько осталось до достижения предела
    """
    @abstractmethod
    def left_until_limit(self, limit_type: LimitType) -> ExchangeLimit:
        pass

    """
    Определеяем не заблокировал ли нас провайдер
    """
    @abstractmethod
    def is_blocked(self) -> bool:
        pass
