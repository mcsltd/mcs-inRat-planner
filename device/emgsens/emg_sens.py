import asyncio
import logging
import time
from enum import Enum

from bleak import BleakClient, BLEDevice

from device.crypt import get_control_sum
from device.emgsens.constants import Command
from device.emgsens.decoder import Decoder
from device.emgsens.structures import Settings

from config import BLE_KEY

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"


class EmgSens:

    UUID_ACQUISITION_SERVICE = "75851135-953a-7739-c781-5a935531397a"
    UUID_DATA_SERVICE = "a397cc38-e8c3-5d7c-9353-31bae53881ff"
    UUID_CHARACTERISTIC_CONTROL = "7395ca15-5997-5a1b-a138-75a7a573b8e5"

    def __init__(self, ble_device: BLEDevice):
        if ble_device is None:
            raise ValueError("BLEDevice не может быть None")

        self._client: BleakClient = BleakClient(ble_device)
        self._connection_state = ConnectionState.DISCONNECTED
        self._is_notifying = False

        # self._disconnection_callback: Optional[Callable] = None

    @property
    def is_connected(self) -> bool:
        return self._connection_state == ConnectionState.CONNECTED

    @property
    def address(self) -> str:
        return self._client.address

    @property
    def is_notifying(self) -> bool:
        return self._is_notifying

    async def connect(self, timeout: float) -> bool:
        """ Подключение к устройству с таймаутом """
        if self.is_connected:
            logger.warning(f"Device {self.address} is already connected")
            return True

        self._connection_state = ConnectionState.CONNECTING
        try:
            await asyncio.wait_for(self._client.connect(), timeout=timeout)
            self._connection_state = ConnectionState.CONNECTED
            # ToDo: set disconnected callback
            logger.info(f"Successfully connected to {self.address}")
        except asyncio.TimeoutError:
            self._connection_state = ConnectionState.DISCONNECTED
            logger.error(f"Connection timeout to {self.address}")
            return False
        except Exception as exp:
            self._connection_state = ConnectionState.DISCONNECTED
            logger.error(f"Failed to connect to {self.address}: {exp}")
            return False
        return True

    async def disconnect(self):
        """ Отключение от устройства """
        if not self.is_connected:
            return
        self._connection_state = ConnectionState.DISCONNECTING
        try:
            await self.stop_acquisition()
            await self._client.disconnect()
            logger.info(f"Disconnected from {self.address}")
        except Exception as exp:
            logger.error(f"Error during disconnect from {self.address}: {exp}")
        finally:
            self._connection_state = ConnectionState.DISCONNECTED

    async def stop_acquisition(self) -> bool:
        """ Остановка получения данных """
        if not self._is_notifying:
            return True

        try:
            if self._client.is_connected:
                await self._client.stop_notify(self.UUID_DATA_SERVICE)
                await self._client.stop_notify(self.UUID_ACQUISITION_SERVICE)
            self._is_notifying = False
            logger.info(f"Stopped acquisition on {self.address}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop acquisition on {self.address}: {e}")
            return False

    async def setup(self, cmd: Command, settings: Settings = b'') -> bool:
        """ Управление подключенным устройством """
        if not self.is_connected:
            logger.error(f"Cannot setup - device {self.address} is not connected")
            return False

        try:
            data = cmd.value.to_bytes() + bytes(settings)
            data += get_control_sum(data=data, key=BLE_KEY)
            await self._client.write_gatt_char(
                EmgSens.UUID_CHARACTERISTIC_CONTROL,
                data, response=True
            )
            logger.debug(f"Setup command {cmd} sent to {self.address}")
            return True

        except Exception as exp:
            logger.error(f"Failed to setup device {self.address}: {exp}")
            return False

    async def start_emg_acquisition(
            self, emg_queue: asyncio.Queue, settings: Settings
    ) -> bool:
        """ Запуск получения ЭМГ данных """
        if self.is_notifying:
            logger.warning(f"Device {self.address} is already notifying")
            return False

        async def emg_handler(_, raw_data: bytearray):
            try:
                counter, emg = decoder.decode_emg(raw_data)
                logger.debug(f"Get emg - counter: {counter}")
                await emg_queue.put({"counter": counter, "emg": emg, "timestamp": time.time()})
            except Exception as exp:
                logger.error(f"Error processing EMG data: {exp}")

        try:
            success = await self.setup(cmd=Command.AcquisitionStart, settings=settings)
            if not success:
                return False

            decoder = Decoder(settings)
            await self._client.start_notify(EmgSens.UUID_ACQUISITION_SERVICE, emg_handler)
            self._is_notifying = True
            logger.info(f"Started EMG acquisition on {self.address}")
            return True

        except Exception as exp:
            logger.error(f"Failed to start EMG acquisition on {self.address}: {exp}")
            return False

    async def start_data_acquisition(
            self, data_queue: asyncio.Queue, settings: Settings
    ) -> bool:
        """ Запуск получения данных """
        if self.is_notifying:
            logger.warning(f"Device {self.address} is already notifying")
            return False

        async def data_handler(_, raw_data: bytearray):
            try:
                counter, e_emg, accel, gyro = decoder.decode_data(raw_data)
                logger.debug(f"Data received - counter: {counter}")

                await data_queue.put({
                    "counter": counter,
                    "e_emg": e_emg,
                    "acceleration": accel,  # in mg
                    "gyro": gyro,  # in mdps
                    "timestamp": time.time()
                })
            except Exception as exp:
                logger.error(f"Error processing data: {exp}")
        try:
            success = await self.setup(cmd=Command.AcquisitionStart, settings=settings)
            if not success:
                return False
            decoder = Decoder(settings)
            await self._client.start_notify(EmgSens.UUID_DATA_SERVICE, data_handler)
            self._is_notifying = True
            logger.info(f"Started data acquisition on {self.address}")
            return True

        except Exception as exp:
            logger.error(f"Failed to start data acquisition on {self.address}: {exp}")
            return False
