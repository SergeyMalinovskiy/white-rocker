from abc import ABC, abstractmethod
from asyncio import Task
from typing import Tuple, Union

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
    def direct_to(self, recipient: Recipient, to: str, message: ISyncMessage) -> IDistributeResponse:
        pass

class IHasMessagesQueue(ABC):
    @abstractmethod
    def push_message(self, message: ISyncMessage) -> None:
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

    @abstractmethod
    def get_err(self) -> Union[str, None]:
        pass

class IAssignableId(ABC):
    @abstractmethod
    def set_id(self, handler_id: HandlerId) -> None:
        pass


class IHasAckMethod(ABC):
    @abstractmethod
    def add_ack_method(self, method: IHasMessagesQueue) -> None:
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
    def add_listener(self, handler: Union[IAssignableId, IHasAckMethod]) -> HandlerId:
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

class IHasUniqueClientId(ABC):
    @abstractmethod
    def get_client_id(self) -> str:
        pass
