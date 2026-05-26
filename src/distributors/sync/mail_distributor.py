import smtplib

from contracts.publisher_service import ICanAuthorized
from contracts.syncer.distributor import ICanDistributeMessage, IDistributeResponse
from contracts.syncer.result import Recipient, ISyncMessage


class MailDistributeResponse(IDistributeResponse):
    def __init__(self, result: str):
        self._result = result

    def result(self) -> str:
        return self._result


class MailDistributor(ICanDistributeMessage, ICanAuthorized):
    def __init__(self,smtp_server: str, smtp_port: int, smtp_user: str, app_pass: str) -> None:
        self._smpt_server = smtp_server
        self._smpt_port   = smtp_port
        self._smtp_user   = smtp_user
        self._smpt_apppass= app_pass
        self._is_authorized = False

    def authorize(self) -> bool:
        return True

    def is_authorized(self) -> bool:
        return self._is_authorized

    def direct_to(self, receiver: Recipient, to: str, message: ISyncMessage) -> IDistributeResponse:
        try:
            with smtplib.SMTP_SSL(self._smpt_server, self._smpt_port) as server:
                server.login(self._smtp_user, self._smpt_apppass)
                server.sendmail(self._smtp_user, to, message.message())
            return MailDistributeResponse("✅ Письмо успешно отправлено!")
        except Exception as e:
            return MailDistributeResponse(f"❌ Ошибка отправки: {e}")
