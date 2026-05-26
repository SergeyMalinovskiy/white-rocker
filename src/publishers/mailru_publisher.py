import asyncio
import imaplib
import email
import json
import os
import time
from asyncio import Task
from email.header import decode_header
from typing import List, Tuple, Union

import requests

from contracts.proxy_object import IAddressable
from contracts.publisher_service import IPublisherService, PollingId, PollerHandler

PollerHash = str
PollerId = int

Poller = tuple[IAddressable, PollerId, PollerHandler, PollerHash]
Pollers = dict[PollingId, Poller]

Sender      = str # идентификатор отправителя
Recipient   = str # идентификатор получателя
Message     = str # сообщение в json формате или строкой
Attachments = List[str] # список полных путей до сохранённых прикрепленных файлов
Ack         = Union[Tuple[str, str], None] # Канал ответа и куда ответить (ack_channel, ack_to)

MailResult = Tuple[Sender, Recipient, Message, Attachments, Ack]

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


class MailRuPublisher(IPublisherService):
    _pollers: Pollers = {}
    _list_locked = False
    _list_counter = 0

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
        self._polling_task: Task|None = None


    def publish(self, address: str, data: bytes, overwrite: bool = True) -> None:
        pass

    def read(self, polling_id: PollingId) -> bytes:
        pass

    def add_poller(self, addressable: IAddressable, polling_rate: int, handler: PollerHandler) -> PollingId:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True

        # TODO: как то надо сделать проверку уникальности добавляемого объекта, но пока N+1 - позже реализовать
        # poller_hash = hashlib.sha1(f'{addressable.get_address()}{id(handler)}'.encode()).hexdigest()

        self._pollers[self._list_counter] = (addressable, polling_rate, handler, '')
        polling_id = self._list_counter
        self._list_counter += 1

        self._list_locked = False

        return polling_id

    def remove_poller(self, polling_id: PollingId) -> None:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True
        self._pollers.pop(polling_id, None)
        self._list_locked = False

    def run(self) -> None:
        self._mail_service.select('EMPP')

        self._is_running = True
        # self._polling_task = asyncio.run(self._listen_worker())
        self._listen_worker()

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

    def _listen_worker(self):
        while self._is_running:
            print('Checking emails...')
            try:
                results = self._check_emails()

                for result in results:
                    sender, recipient, data, attachments, ack = result

                    if recipient == 'finalazer/store-card':

                        api_route = 'http://finalazer.local:9001/api/v1/cards'

                        if len(attachments) > 0:
                            with open(attachments[0], 'rb') as image:
                                response = requests.post(
                                    api_route,
                                    files={
                                        'image': (attachments[0], image),
                                    }
                                )

                                print(response.text)
            except:
                pass

            time.sleep(_DELAY)


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

                subject = _decode_str(msg.get('Subject', ''))
                from_addr = _decode_str(msg.get('From', ''))

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
                mails_results.append((
                    body.get('iam'),
                    body.get('for'),
                    body.get('data'),
                    attachments,
                    (body.get('ack_channel'), body.get('ack_to')) if ack_valid else None,
                ))

            # self._mail_service.close()

        return mails_results


