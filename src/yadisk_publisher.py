import json
import os.path
import time
from http.client import responses
from pathlib import Path
from typing import Any

import requests

from src.proxy_object import ProxyObject

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


class YaDiskPublisher:

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


    def authorize(self) -> bool:
        self._token = self._get_token()

        print({'Token': self._token})



    def is_authorized(self) -> bool:
        return self._is_authorized | bool(self._access_token)

    def publish(self, file_path: str, filename: str, overwrite=True) -> ProxyObject:
        pass

    def check(self, proxy_object: ProxyObject) -> bool:
        pass

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