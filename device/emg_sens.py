import hashlib
import asyncio
import logging

from typing import Optional
from bleak import BleakClient, BLEDevice
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher


from device.structures import Settings

logger = logging.getLogger(__name__)

def get_control_sum(data: bytes, key: bytearray) -> bytes:
    """ Data signing before writing in characteristic """
    hash = hashlib.sha256(data).digest()
    iv = bytes(128 // 8)
    # create encoder
    cipher = Cipher(
        algorithm=algorithms.AES(key), mode=modes.CBC(iv)
    )
    encryptor = cipher.encryptor()
    # encrypt
    sign = encryptor.update(hash) + encryptor.finalize()
    return sign


class EmgSens:
    def __init__(
            self,
            ble_device: BLEDevice,
    ):
        self.device = ble_device
        self._client: Optional[BleakClient] = None

        # set lock
        self._connect_lock = asyncio.Lock()
        self._operation_lock = asyncio.Lock()

    async def setup(self, settings: Settings):
        pass

