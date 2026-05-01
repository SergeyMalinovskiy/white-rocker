import hashlib

from contracts.proxy_object import IHasData, IAddressable, DataHash


class ImageProxy(IHasData, IAddressable):
    _hash: DataHash = 0

    def __init__(self, data: bytes, address: str) -> None:
        self._update_data(data)
        self._address = address

    def get_address(self) -> str:
        return self._address

    def set_data(self, data: bytes) -> None:
        self._update_data(data)

    def get_data(self) -> bytes:
        return self._data

    def get_hash(self) -> DataHash:
        return self._hash

    def _update_data(self, data: bytes) -> None:
        self._hash = hashlib.md5(data).hexdigest()
        self._data = data
