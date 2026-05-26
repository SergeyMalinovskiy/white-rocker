from abc import ABC, abstractmethod
from typing import List, Union

from contracts.syncer.ack import IContainsAssignment


Sender = str
Recipient = str

class ISyncMessage(ABC):

    @abstractmethod
    def sender(self) -> Sender:
        pass

    @abstractmethod
    def receiver(self) -> Recipient:
        pass

    @abstractmethod
    def message(self) -> str:
        pass

    @abstractmethod
    def attachments(self) -> List[str]:
        pass

    @abstractmethod
    def ack(self) -> Union[IContainsAssignment, None]:
        pass

    @abstractmethod
    def hashsum(self) -> str:
        pass

    @abstractmethod
    def send_time(self) -> str: #формат Ymd_His
        pass
