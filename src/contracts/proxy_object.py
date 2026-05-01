from abc import ABC, abstractmethod

DataHash = str

class IHasData(ABC):
    @abstractmethod
    def get_data(self) -> bytes:
        pass

    @abstractmethod
    def set_data(self, data: bytes) -> None:
        pass

    @abstractmethod
    def get_hash(self) -> DataHash:
        pass

class IAddressable(ABC):
    @abstractmethod
    def get_address(self) -> str:
        pass
