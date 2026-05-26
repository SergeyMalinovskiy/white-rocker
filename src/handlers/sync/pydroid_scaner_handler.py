from contracts.syncer.distributor import IContainsHandleResult, ICanHandleIncomingMessage, HandlerId, HandleResult, \
    ICanDistributeMessage, IAssignableId
from contracts.syncer.result import ISyncMessage
from handlers.sync.idle_handler import IdleHandleResult


class PydroidScannerHandleResult(IContainsHandleResult):
    def __init__(self, handler_id: HandlerId, message: ISyncMessage, is_handled: bool = False):
        self._handler_id = handler_id
        self._message = message
        self._is_handled = is_handled

    def get_result(self) -> HandleResult:
        return IdleHandleResult(self._handler_id, self._message).get_result()

    def is_handled(self) -> bool:
        return self._is_handled


class PydroidScannerHandler(ICanHandleIncomingMessage, IAssignableId):
    def __init__(self, distributor: ICanDistributeMessage) -> None:
        self._distributor = distributor
        self._handler_id = None

    def get_id(self) -> HandlerId:
        return self._handler_id

    def set_id(self, handler_id: HandlerId) -> None:
        self._handler_id = handler_id

    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        self._distributor.direct_to(message.receiver(), message)

        return PydroidScannerHandleResult(self._handler_id, message)
