import hashlib
import json
import os.path
import time
from pathlib import Path

import requests

from contracts.proxy_object import IAddressable
from src.contracts.publisher_service import IPublisherService, PollingId, PollerHandler

_DEFAULT_DESTINATION = "/animal_photos"
_CACHE_TOKEN_PATH='yadisk_token.json'


def check_token(received_at: int, expires_in: int) -> bool:
    try:
        return int(time.time()) < received_at + expires_in
    except Exception as e:
        return False


def is_token(token) -> bool:
    return (
            type(token) is dict
            and bool(token.get('access_token', False))
            and bool(token.get('refresh_token', False))
            and bool(token.get('expires_in', False))
            # and token.get('received_at', False)
    )

_REQUESTS_LIMIT = 5

PollerHash = str
PollerId = int

Poller = tuple[IAddressable, PollerId, PollerHandler, PollerHash]
Pollers = dict[PollingId, Poller]

class YaDiskPublisher(IPublisherService):
    def read(self, polling_id: PollingId) -> bytes:
        pass

    _pollers: Pollers = {}
    _list_locked = False
    _list_counter = 0

    def add_poller(self, addressable: IAddressable, polling_rate: int, handler: PollerHandler) -> PollingId:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True

        # TODO: как то надо сделать проверку уникальности добавляемого объекта, но пока N+1 - позже реализовать
        # poller_hash = hashlib.sha1(f'{addressable.get_address()}{id(handler)}'.encode()).hexdigest()

        self._pollers[self._list_counter] = (addressable, polling_rate, handler, '')
        polling_id = self._list_counter
        self._list_counter+=1

        self._list_locked = False

        return polling_id

    def remove_poller(self, polling_id: PollingId) -> None:
        if self._list_locked:
            raise RuntimeError('Record is failed, list already locked')

        self._list_locked = True
        self._pollers.pop(polling_id, None)
        self._list_locked = False

    def __init__(
        self,
        host: str,
        oauth: str,
        client_id: str,
        client_secret: str,
        verification_code: str,
        cache_path: str,
    ) -> None:
        self._host = host
        self._oauth = oauth

        self._client_id = client_id
        self._client_secret = client_secret
        self._verification_code = verification_code

        self._token = None
        self._is_authorized = False
        self._cache_path = cache_path


    def authorize(self) -> None:
        self._token = self._get_token()

        # print({'Token': self._token})


    def is_authorized(self) -> bool:
        return self._is_authorized | bool(self._token)

    def publish(self, address: str, data: bytes, overwrite: bool = True) -> None:
        print(f'Publishing "{address}"..."')
        response = requests.get(
            url=f"{self._host}/upload",
            headers={
                'Authorization': f'OAuth {self._token.get('access_token')}',
            },
            params={
                'path': f"{_DEFAULT_DESTINATION}/{address}",
                'overwrite': overwrite,
            }
        )
        response_data = response.json()
        upload_href = response_data.get('href')

        upload_response = requests.put(url=upload_href, files={'file': data})

        print(upload_response.json())

    def get_pollers(self) -> Pollers:
        return self._pollers

    def _get_token(self, ignore_cache: bool = False) -> dict:
        token = self._load_token_from_cache() if not ignore_cache else None

        is_token_valid = (is_token(token)
            and token.get('received_at', False)
            and check_token(token.get('received_at'), token.get('expires_in'))
        )

        return token if is_token_valid else self._request_token()


    def _handle_error(self, error):
        match error.get('error_description'):
            case 'Invalid code':
                self._update_your_verification_code_handle_error()
            case 'Code has expired':
                self._update_your_verification_code_handle_error()
            case _:
                print(error)

    def _update_your_verification_code_handle_error(self):
        print(
            'Update your verification code: {}'.format(
                self._oauth + '/authorize?response_type=token&client_id=' + self._client_id
            )
        )

    def _load_token_from_cache(self) -> dict | None:
        try:
            return json.loads(
                Path(os.path.join(self._cache_path, _CACHE_TOKEN_PATH)).read_text()
            )
        except Exception as e:
            print(e)

            return None

    def _request_token(self) -> dict | None:
        data = {
            'grant_type': 'authorization_code',
            'code': self._verification_code,
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'redirect_uri': 'https://oauth.yandex.ru/verification_code',
        }

        try:
            response = requests.post(self._oauth + '/token', data=data)

            response_data = response.json()

            if response_data.get('error', False):
                self._handle_error(response_data)

            if is_token(response_data):
                token = response_data.set('received_at', int(time.time()))

                return token

        except requests.exceptions.RequestException as e:
            print({
                'error': str(e),
            })


    def _refresh_token(self) -> dict:
        pass

    def get_metadata(self, address: str) -> None:
        if not self._is_authorized:
            raise RuntimeError('Request is not authorized')

        try:
            response = requests.get(
                url=f"{self._host}",
                params={
                    'path': f"{_DEFAULT_DESTINATION}/{address}",
                    # 'fields': '',
                    'limit': 1,
                },
                headers={
                    'Authorization': f'OAuth {self._token.get('access_token')}',
                },
            )

            print(response.json())

        except requests.exceptions.RequestException as e:
            print({
                'error': str(e),
            })

    def run(self) -> None:
        pass