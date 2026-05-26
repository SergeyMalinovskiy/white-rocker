from abc import ABC, abstractmethod
from asyncio import Task
from typing import Tuple

from contracts.syncer.ack import IContainsAssignment
from contracts.syncer.result import Recipient, ISyncMessage

HandlerId = int

HandleResult = dict

class IDistributeResponse(ABC):
    @abstractmethod
    def result(self) -> str:
        pass


class ICanDistributeMessage(ABC):
    @abstractmethod
    def direct_to(self, receiver: Recipient, to: str, message: ISyncMessage) -> IDistributeResponse:
        pass

class IContainsHandleResult(ABC):


    """
    Может ли обработчик обработать это сообщение
    """
    @abstractmethod
    def is_handled(self) -> bool:
        pass

    """
    Результат работы обработчика
    """
    @abstractmethod
    def get_result(self) -> HandleResult:
        pass

class IAssignableId(ABC):
    @abstractmethod
    def set_id(self, handler_id: HandlerId) -> None:
        pass

class ICanHandleIncomingMessage(ABC):
    @abstractmethod
    def get_id(self) -> HandlerId:
        pass

    @abstractmethod
    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        pass


class ICanListeningIncomingMessages(ABC):
    @abstractmethod
    def add_listener(self, handler: IAssignableId) -> HandlerId:
        pass

    @abstractmethod
    def remove_listener(self, handler_id: HandlerId) -> None:
        pass

    @abstractmethod
    def listen(self) -> None:
        pass

    @abstractmethod
    def async_listen(self) -> Task:
        pass
