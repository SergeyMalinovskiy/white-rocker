from abc import ABC, abstractmethod

Channel = str

class IContainsAssignment(ABC):

    """
    Канал для отправки ответа отправителю
    """
    @abstractmethod
    def channel(self) -> Channel:
        pass

    """
    Кому перенаправить ответ.
    Чисто теоретически ответ может получить другой получатель (поручитель), но если получатель имеет поручение на обработку ответа и может его обработать
    """
    @abstractmethod
    def to(self) -> str:
        pass

    # @abstractmethod
    # def hash(self) -> str:
    #     pass

