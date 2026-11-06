from typing import Union

from contracts.syncer.distributor import ICanDistributeMessage, ICanHandleIncomingMessage, IAssignableId, HandlerId, \
    IContainsHandleResult, HandleResult
from contracts.syncer.result import ISyncMessage


_FINALAZER_ID = 'finalazer'

class FinalazerHandleResult(IContainsHandleResult):
    def __init__(self, handler_id: HandlerId, message: ISyncMessage, is_handled: bool = False, err = None) -> None:
        self._handler_id = handler_id
        self._message = message
        self._is_handled = is_handled
        self._err = err

    def is_handled(self) -> bool:
        return self._is_handled

    def get_result(self) -> HandleResult:
        return {
            "id": self._handler_id,
            "sender": self._message.sender,
            "receiver": self._message.recipient,
            "message": self._message.message,
            "attachments": self._message.attachments,
        }

    def get_err(self) -> Union[str, None]:
        return self._err


class FinalazerHandler(ICanHandleIncomingMessage, IAssignableId):
    def __init__(self, distributor: ICanDistributeMessage) -> None:
        self._handler_id = None
        self._distributor = distributor

    def get_id(self) -> HandlerId:
        return self._handler_id

    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        recipient, to = message.recipient().split('/')
        if recipient != _FINALAZER_ID:
            return FinalazerHandleResult(self._handler_id, message)

        try:
             self._distributor.direct_to(recipient, to, message)
        except Exception as e:
            return FinalazerHandleResult(self._handler_id, message, is_handled=True, err=str(e))

        return FinalazerHandleResult(self._handler_id, message, is_handled=True)

        return FinalazerHandleResult(handler_id=self._handler_id, message=message, is_handled=True)

    def set_id(self, handler_id: HandlerId) -> None:
        self._handler_id = handler_id
