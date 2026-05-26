from contracts.syncer.distributor import ICanHandleIncomingMessage, HandlerId, IContainsHandleResult, HandleResult, \
    IAssignableId
from contracts.syncer.result import ISyncMessage

class IdleHandleResult(IContainsHandleResult):
    def __init__(self, handler_id: HandlerId, message: ISyncMessage, is_handled: bool = False) -> None:
        self._handler_id = handler_id
        self._message = message
        self._is_handled = is_handled

    def get_result(self) -> HandleResult:
        return {
            "id": self._handler_id,
            "sender": self._message.sender,
            "receiver": self._message.receiver,
            "message": self._message.message,
            "attachments": self._message.attachments,

        }

    def is_handled(self) -> bool:
        return self._is_handled


class SyncIdleHandler(ICanHandleIncomingMessage, IAssignableId):
    def __init__(self):
        self._handler_id = None

    def get_id(self) -> HandlerId:
        return self._handler_id

    def set_id(self, handler_id: HandlerId) -> None:
        self._handler_id = handler_id

    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        return IdleHandleResult(handler_id=self._handler_id, message=message)