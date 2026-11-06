from datetime import datetime
from typing import Union

from contracts.syncer.distributor import IContainsHandleResult, ICanHandleIncomingMessage, IAssignableId, HandlerId, \
    ICanDistributeMessage, HandleResult, IHasUniqueClientId, IHasAckMethod, IHasMessagesQueue
from contracts.syncer.result import ISyncMessage, Sender, Recipient
from publishers.mail_publisher import MailResult


class ClientHandlerResult(IContainsHandleResult):
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
            'ack': self._message.ack,
            'err': self._err,
        }

    def get_err(self) -> Union[str, None]:
        return self._err


class ClientHandler(ICanHandleIncomingMessage, IAssignableId, IHasUniqueClientId, IHasAckMethod):
    def __init__(self, client_id: str, distributor: ICanDistributeMessage) -> None:
        self._distributor = distributor
        self._handler_id = None
        self._client_id = client_id
        self._ack_method: Union[IHasMessagesQueue, None] = None

    def get_client_id(self) -> str:
        return self._client_id

    def get_id(self) -> HandlerId:
        return self._handler_id

    def set_id(self, handler_id: HandlerId) -> None:
        self._handler_id = handler_id

    def handle(self, message: ISyncMessage) -> IContainsHandleResult:
        recipient, to = message.recipient().split('/')
        if message.recipient().split('/')[0] != self._client_id:
            return ClientHandlerResult(self._handler_id, message)

        try:
            response = self._distributor.direct_to(recipient, to, message)

            ack_assignment = message.ack()
            if ack_assignment and self._ack_method is not None:
                self.ack(
                    message.recipient(),
                    ack_assignment.to(),
                    response.result(),
                )

        except Exception as e:
            print(e)
            return ClientHandlerResult(self._handler_id, message, is_handled=True, err=str(e))

        return ClientHandlerResult(self._handler_id, message, is_handled=True)

    def add_ack_method(self, method: IHasMessagesQueue) -> None:
        self._ack_method = method

    def ack(self, sender: Sender, recipient: Recipient, data: str) -> None:
        ack_message = MailResult(
            sender=sender,
            recipient=recipient,
            message=data,
            attachments=[],
            ack=None,
            hashsum='',
            send_time=datetime.now().strftime('%Y%m%d_%H%M%S'),
        )

        self._ack_method.push_message(ack_message)


