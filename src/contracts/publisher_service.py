from abc import ABC, abstractmethod
from typing import Callable

from contracts.proxy_object import IHasData, IAddressable

# from src.contracts.proxy_object import IProxyObject

PollingId = int

PollerHandler = Callable[[IHasData], None]

class ICanAuthorized(ABC):
    @abstractmethod
    def authorize(self) -> bool:
        pass

    @abstractmethod
    def is_authorized(self) -> bool:
        pass

class IPublisherService(ICanAuthorized):

    @abstractmethod
    def publish(self, address: str, data: bytes, overwrite: bool = True) -> None:
        pass

    @abstractmethod
    def read(self, polling_id: PollingId) -> bytes:
        pass

    @abstractmethod
    def add_poller(self, addressable: IAddressable, polling_rate: int, handler: PollerHandler) -> PollingId:
        pass

    @abstractmethod
    def remove_poller(self, polling_id: PollingId) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass
