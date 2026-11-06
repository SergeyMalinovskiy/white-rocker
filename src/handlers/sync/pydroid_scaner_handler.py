from typing import Union

from contracts.syncer.distributor import IContainsHandleResult, ICanHandleIncomingMessage, HandlerId, HandleResult, \
    ICanDistributeMessage, IAssignableId
from contracts.syncer.result import ISyncMessage
from handlers.sync.idle_handler import IdleHandleResult

_PYDROID_SCANER_ID = 'pydroid-scaner'

class PydroidScanerHandleResult(IContainsHandleResult):
    def __init__(self, handler_id: HandlerId, message: ISyncMessage, is_handled: bool = False, err = None):
        self._handler_id = handler_id
        self._message = message
        self._is_handled = is_handled
        self._err = err

    def get_result(self) -> HandleResult:
        return IdleHandleResult(self._handler_id, self._message).get_result()

    def is_handled(self) -> bool:
        return self._is_handled

    def get_err(self) -> Union[str, None]:
        return self._err


class PydroidScannerHandler(ICanHandleIncomingMessage, IAssignableId):
    def __init__(self, distributor: ICanDistributeMessage) -> None:
        self._distributor = distributor
        self._handler_id = None

    def get_id(self) -> HandlerId:
        return self._handler_id

    def set_id(self, handler_id: HandlerId) -> None:
        self._handler_id = handler_id

    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        recipient, to = message.recipient().split('/')
        if message.recipient().split('/')[0] != _PYDROID_SCANER_ID:
            return PydroidScanerHandleResult(self._handler_id, message)

        try:
            self._distributor.direct_to(recipient, to, message)
        except Exception as e:
            return PydroidScanerHandleResult(self._handler_id, message, is_handled=True, err=str(e))

        return PydroidScanerHandleResult(self._handler_id, message, is_handled=True)
