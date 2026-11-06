from typing import Dict, Callable

import requests

from contracts.publisher_service import ICanAuthorized
from contracts.syncer.distributor import ICanDistributeMessage, IDistributeResponse
from contracts.syncer.result import Recipient, ISyncMessage


class FinalazerDistibuteResponse(IDistributeResponse):
    def __init__(self, response: str) -> None:
        self._result = response

    def result(self) -> str:
        return self._result


class FinalazerDistributor(ICanDistributeMessage, ICanAuthorized):
    def __init__(self,host: str, port: int, token: str):
        self._host = host
        self._port = port
        self._token = token

        self._is_authorized = False

        self._base_uri = f"http://{host}:{port}/api/v1"

        self._ACTION_MAP: Dict[str, Callable[[ISyncMessage], IDistributeResponse]] = {
            'store-card': self._store_card_action,
        }

    def direct_to(self, recipient: Recipient, to: str, message: ISyncMessage) -> IDistributeResponse:
        action = self._ACTION_MAP.get(to, None)
        if action is None:
            return FinalazerDistibuteResponse('Error: action not found.')


        action_res = None
        try:
            action_res = action(message)
        except Exception as e:
            print(e)


        print('Finalazer distributor', action_res.result())

        return action_res


    def authorize(self) -> bool:
        return True

    def is_authorized(self) -> bool:
        return self._is_authorized

    def _store_card_action(self, message: ISyncMessage) -> IDistributeResponse:
        attachments = message.attachments()

        if len(attachments) > 0:
            with open(attachments[0], 'rb') as image:
                response = requests.post(
                    f"{self._base_uri}/cards",
                    files={
                        'image': (attachments[0], image),
                    }
                )

                return FinalazerDistibuteResponse(response.text)

        return FinalazerDistibuteResponse('Error: attachments are required.')


