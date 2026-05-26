import email
import hashlib
import imaplib
import json
import os
import time
from email.header import decode_header
from typing import Union, List
from datetime import datetime

from _asyncio import Task

from contracts.publisher_service import ICanAuthorized
from contracts.syncer.ack import IContainsAssignment, Channel
from contracts.syncer.distributor import ICanListeningIncomingMessages, HandlerId, ICanHandleIncomingMessage, \
    IAssignableId
from contracts.syncer.result import ISyncMessage, Recipient, Sender

Listeners = dict[HandlerId, Union[ICanHandleIncomingMessage, IAssignableId]]

class DefaultAckAssignment(IContainsAssignment):
    def __init__(self, channel: str, to: str) -> None:
        self._channel = channel
        self._to = to

    def channel(self) -> Channel:
        return self._channel

    def to(self) -> str:
        return self._to


class MailResult(ISyncMessage):
    def __init__(
            self,
            sender: Sender,
            recipient: Recipient,
            message: str,
            attachments: List[str],
            ack: IContainsAssignment,
            hashsum: str,
            send_time: str,
    ) -> None:
        self._sender = sender
        self._recipient = recipient
        self._message = message
        self._attachments = attachments
        self._ack = ack
        self._hashsum = hashsum
        self._send_time = send_time


    def sender(self) -> Sender:
        return self._sender

    def receiver(self) -> Recipient:
        return self._recipient

    def message(self) -> str:
        return self._message

    def attachments(self) -> List[str]:
        return self._attachments

    def ack(self) -> Union[IContainsAssignment, None]:
        return self._ack

    def send_time(self) -> str:
        return self._send_time

    def hashsum(self):
        return self._hashsum

    def __dict__(self) -> dict:
        return {
            'sender': self._sender,
            'recipient': self._recipient,
            'message': self._message,
            'attachments': self._attachments,
            'ack': (self._ack.channel(), self._ack.to()) if self._ack else None,
            'send_at': self._send_time,
            'hashsum': self._hashsum,
            'is_verified': self._hashsum == self.__hash__()
        }

    def __hash__(self):
        ord_bytes =  b''.join(
            ord(ch).to_bytes(2, 'big') for ch in f"{self._sender}{self._recipient}{self._message}{len(self._attachments)}{self._send_time}"
        )
        return hashlib.sha256(ord_bytes).hexdigest()


_DELAY = 10 # sec


def _decode_str(text):
    """Декодирование заголовков"""
    if text is None:
        return ''
    decoded_parts = decode_header(text)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            charset = charset or 'utf-8'
            try:
                part = part.decode(charset, errors='ignore')
            except:
                part = part.decode('utf-8', errors='ignore')
        result.append(str(part))
    return ' '.join(result)


def _get_email_body(msg) -> str:
    """
    Извлечение текстового тела письма
    Возвращает обычный текст (plain text) или HTML (если plain нет)
    """
    body = ""

    if msg.is_multipart():
        # Письмо состоит из нескольких частей
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Пропускаем вложения
            if "attachment" in content_disposition:
                continue

            # Берём текстовую часть
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif content_type == "text/html" and not body:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        # Простое письмо (не multipart)
        content_type = msg.get_content_type()
        if content_type == "text/plain" or content_type == "text/html":
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    return body


class MailPublisher(ICanListeningIncomingMessages, ICanAuthorized):
    _listeners: Listeners  = {}
    _list_locked = False
    _list_counter = 0
    _is_authorized = False

    def __init__(
            self,
            imap_host: str,
            imap_port: int,
            imap_username: str,
            imap_password: str,
            sender_address: str,
            receiver_address: str,
            attachments_dir: str,
    ):
        print(imap_host, imap_port, imap_username, imap_password)
        self._mail_service = None
        self._imap_host = imap_host
        self._imap_port = imap_port
        self._imap_username = imap_username
        self._imap_password = imap_password
        self._sender_address = sender_address
        self._recipient_address = receiver_address
        self._attachments_dir = attachments_dir

        self._is_running = False

    def authorize(self) -> bool:
        self._mail_service = imaplib.IMAP4_SSL(self._imap_host, self._imap_port)

        ok, *_ = self._mail_service.login(self._imap_username, self._imap_password)

        print('MAILRU LOGIN', (ok, *_))

        if ok == 'OK':
            self._is_authorized = True
            return True
        else:
            return False

    def is_authorized(self) -> bool:
        return self._is_authorized

    def get_listeners(self) -> Listeners:
        return self._listeners

    def add_listener(self, handler: IAssignableId) -> HandlerId:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True

        # TODO: как то надо сделать проверку уникальности добавляемого объекта, но пока N+1 - позже реализовать
        # poller_hash = hashlib.sha1(f'{addressable.get_address()}{id(handler)}'.encode()).hexdigest()

        handler_id = self._list_counter
        handler.set_id(handler_id)
        self._listeners[handler_id] = handler
        self._list_counter += 1

        self._list_locked = False

        return handler_id

    def remove_listener(self, handler_id: HandlerId) -> None:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True
        self._listeners.pop(handler_id, None)
        self._list_locked = False

    def listen(self) -> None:
        self._mail_service.select('EMPP')

        self._is_running = True
        # self._polling_task = asyncio.run(self._listen_worker())

        self._listen_worker()

    def async_listen(self) -> Task:
        pass

    def _listen_worker(self):
        try:
            while self._is_running:
                print(f"[{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] Checking emails...")

                self._check()

                time.sleep(_DELAY)
        except KeyboardInterrupt as ki:
            print("Exiting...")


    def _check(self):

        results = self._check_emails()

        for result in results:
            print(result.__dict__())

    def _check_emails(self) -> List[MailResult]:
        mails_results: List[MailResult] = []
        # Используем контекстный менеджер для подключения
        status, messages = self._mail_service.search(None, 'UNSEEN')
        # status, messages = self._mail_service.search(None, 'ALL')
        if status == 'OK' and messages[0]:
            email_ids = messages[0].split()
            print(f"📬 Найдено писем в папке: {len(email_ids)}")

            for email_id in email_ids:
                # Обработка каждого письма
                status, msg_data = self._mail_service.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                #
                # subject = _decode_str(msg.get('Subject', ''))
                # from_addr = _decode_str(msg.get('From', ''))

                body = json.loads(_get_email_body(msg))
                attachments = []
                if msg.is_multipart():
                    for part in msg.walk():
                        # Проверяем, является ли часть вложением
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        filename = part.get_filename()
                        if filename:
                            # Декодируем имя файла (может быть закодировано)
                            filename = _decode_str(filename)

                            # Создаём папку если её нет
                            os.makedirs(self._attachments_dir, exist_ok=True)

                            # Формируем полный путь
                            filepath = os.path.join(self._attachments_dir, filename)

                            print(filepath)

                            # Сохраняем файл
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                attachments.append(filepath)

                # MailResult = Tuple[Sender, Recipient, Message, Attachment, AckChannel, AckTo]
                ack_valid = (bool)(body.get('ack_channel', False)) | (bool)(body.get('ack_to', False))
                mails_results.append(MailResult(
                    body.get('iam'),
                    body.get('for'),
                    body.get('data'),
                    attachments,
                    DefaultAckAssignment(body.get('ack_channel'), body.get('ack_to')) if ack_valid else None,
                    body.get('hashsum'),
                    body.get('send_time'),
                ))
                # mails_results.append((
                #     body.get('iam'),
                #     body.get('for'),
                #     body.get('data'),
                #     attachments,
                #     (body.get('ack_channel'), body.get('ack_to')) if ack_valid else None,
                # ))

            # self._mail_service.close()

        return mails_results
