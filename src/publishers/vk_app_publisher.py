from contracts.proxy_object import IAddressable
from contracts.publisher_service import IPublisherService, PollingId, PollerHandler


class VkAppPublisher(IPublisherService):
    def __init__(self, private_key: str, service_key) -> None:
        self._private_key = private_key
        self._service_key = service_key

    def authorize(self):
        pass

    def is_authorized(self) -> bool:
        return False

    def publish(self, address: str, data: bytes, overwrite: bool = True) -> None:
        pass

    def read(self, polling_id: PollingId) -> bytes:
        pass

    def add_poller(self, addressable: IAddressable, polling_rate: int, handler: PollerHandler) -> PollingId:
        pass

    def remove_poller(self, polling_id: PollingId) -> None:
        pass

    def run(self) -> None:
        pass
