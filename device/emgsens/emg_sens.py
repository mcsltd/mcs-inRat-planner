import hashlib
import asyncio
import logging

from typing import Optional
from bleak import BleakClient, BLEDevice

from device.crypt import get_control_sum
from device.emgsens.constants import Command
from device.emgsens.decoder import Decoder
from device.emgsens.structures import Settings

from config import BLE_KEY

logger = logging.getLogger(__name__)

class EmgSens:

    UUID_ACQUISITION_SERVICE = "75851135-953a-7739-c781-5a935531397a"
    UUID_DATA_SERVICE = "a397cc38-e8c3-5d7c-9353-31bae53881ff"
    UUID_CHARACTERISTIC_CONTROL = "7395ca15-5997-5a1b-a138-75a7a573b8e5"

    def __init__(self, ble_device: BLEDevice):

        if ble_device is None:
            raise ValueError("Device not found.")

        self._client: BleakClient = BleakClient(ble_device)

        self.is_connected = self._client.is_connected

    async def setup(self, cmd: Command, settings: Settings = b''):
        if not self.is_connected:
            raise ValueError(f"{self._client} is not connected!")

        # ToDo self._check_operation_lock()

        data = cmd.value.to_bytes() + bytes(settings)
        data += get_control_sum(data=data, key=BLE_KEY)
        await self._client.write_gatt_char(EmgSens.UUID_CHARACTERISTIC_CONTROL, data)


    async def connect(self):
        await self._client.connect()
        logger.debug(f"{self._client.address} is connected.")
        self.is_connected = self._client.is_connected

    async def disconnect(self):
        logger.debug(f"{self._client.address} is disconnected.")
        await self._client.disconnect()
        self.is_connected = self._client.is_connected

    async def get_data(self, data_queue, settings):
        """ Subscribe and get data from ble service """
        async def data_handler(_, raw_data: bytearray):
            counter, e_emg, accel, gyro = decoder.decode_data(raw_data)
            logger.info(f"Get data - counter: {counter}")
            # put data in async queue
            await data_queue.put({
                "counter": counter,
                "e_emg": e_emg,
                "acceleration": accel,  # in mg
                "gyro": gyro  # in mdps
            })
        await self.setup(cmd=Command.AcquisitionStart, settings=settings)
        decoder = Decoder(settings)
        await self._client.start_notify(EmgSens.UUID_DATA_SERVICE, data_handler)
