from abc import ABC, abstractmethod


class IChannel(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass
