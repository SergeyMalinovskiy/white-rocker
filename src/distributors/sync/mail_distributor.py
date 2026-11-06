import datetime
import json
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from contracts.publisher_service import ICanAuthorized
from contracts.syncer.distributor import ICanDistributeMessage, IDistributeResponse
from contracts.syncer.result import Recipient, ISyncMessage


class MailDistributeResponse(IDistributeResponse):
    def __init__(self, result: str):
        self._result = result

    def result(self) -> str:
        return self._result


class MailDistributor(ICanDistributeMessage, ICanAuthorized):
    def __init__(self,smtp_server: str, smtp_port: int, smtp_user: str, app_pass: str, recipient: str) -> None:
        self._smpt_server = smtp_server
        self._smpt_port   = smtp_port
        self._smtp_user   = smtp_user
        self._smpt_apppass= app_pass
        self._recipient = recipient
        self._is_authorized = False

    def authorize(self) -> bool:
        return True

    def is_authorized(self) -> bool:
        return self._is_authorized

    def direct_to(self, recipient: Recipient, to: str, message: ISyncMessage) -> IDistributeResponse:
        print(f"Отправляем письмо pydroid-scaner", recipient, to, message.message())

        msg = MIMEMultipart()
        msg['From'] = self._smtp_user
        msg['To'] = self._recipient
        msg['Subject'] = Header(f"[EMPP][{message.send_time()}]", 'utf-8')

        print('test')

        msg.attach(MIMEText(json.dumps({
            'iam': message.sender(),
            'for': message.recipient(),
            'hashsum': message.hashsum(),
            'send_time': message.send_time(),
            'data': message.message(),
        }), 'plain', 'utf-8'))

        try:
            with smtplib.SMTP_SSL(self._smpt_server, self._smpt_port) as server:
                server.login(self._smtp_user, self._smpt_apppass)
                server.send_message(msg)
            return MailDistributeResponse("✅ Письмо успешно отправлено!")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return MailDistributeResponse(f"❌ Ошибка отправки: {e}")
