import asyncio
import ctypes
import hashlib
import logging
import time
from enum import IntEnum
from functools import cached_property
from uuid import UUID

from bleak import BLEDevice, BleakClient
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from src.config import BLE_KEY_IN_RAT
from src.device.inrat_v1.decoder import decode_ecg
from src.device.inrat_v1.enums import Command, EnabledChannels, EventType, SamplingRate, ScaleAccelerometer
from src.device.inrat_v1.structures import Settings, Event, Status

BLE_KEY = BLE_KEY_IN_RAT


logger = logging.getLogger(__name__)



def get_control_sum(data: bytes, key: bytearray) -> bytes:
    """ Вспомогательная функция получения контрольной суммы """
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


class inRat:

    UUID_CHARACTERISTIC_DATA_ECG = "59573ef1-5389-575f-87d5-5f31fcdcba7b"
    UUID_CHARACTERISTIC_EVENT = "f553739f-9f1f-538d-a7d3-cd987b395eb5"
    UUID_CHARACTERISTIC_CONTROL = "7395ca15-5997-5a1b-a138-75a7a573b8e5"
    UUID_CHARACTERISTIC_STATUS = "c3571b1b-e17e-5195-9fd3-8119cb153187"

    UUID_TEMPLATE = "0000{:0>4x}-0000-1000-8000-00805f9b34fb"
    class inRatCharacteristic(IntEnum):
        MANUFACTURER_NAME = 0x2A29
        MODEL = 0x2A24
        SERIAL = 0x2A25
        FIRMWARE = 0x2A26
        HARDWARE = 0x2A27

        @cached_property
        def uuid(self) -> UUID:
            """Convert the ID to a full UUID and cache."""
            return UUID(inRat.UUID_TEMPLATE.format(self.value))

        def __str__(self) -> str:
            """Convert UUID to string value."""
            return str(self.uuid)

    def __init__(self, ble_device: BLEDevice):
        self._client: BleakClient = BleakClient(ble_device)

        # свойства для настройки и запуска inrat
        self._is_activated: None | bool = None
        self._is_notifying = False
        self._sampling_rate = SamplingRate.HZ_500
        self._high_pass_filter_ecg: int = 0
        self._full_scale_accelerometer = ScaleAccelerometer.G_2
        self._activity_threshold = 1

        # свойства устройства
        self._name = ble_device.name
        self._address = ble_device.address
        self._manufacturer = None
        self._model = None
        self._serial = None
        self._firmware = None
        self._hardware = None


    # свойства клиента
    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    @property
    def is_activated(self):
        return self._is_activated

    # свойства полученные от подключенного устройства
    @property
    def name(self) -> str | None:
        return self._name
    @property
    def manufacturer(self) -> str | None:
        return self._manufacturer
    @property
    def model(self) -> str | None:
        return self._model
    @property
    def serial(self) -> str | None:
        return self._serial
    @property
    def hardware(self) -> str | None:
        return self._hardware
    @property
    def firmware(self) -> str | None:
        return self._firmware
    @property
    def address(self) -> str | None:
        return self._address

    # свойства для настройки подключенного устройства
    @property
    def sampling_rate(self) -> None | float:
        if self._sampling_rate == SamplingRate.HZ_500:
            return 500.0
        if self._sampling_rate == SamplingRate.HZ_1000:
            return 1000.0
        if self._sampling_rate == SamplingRate.HZ_2000:
            return 2000.0
        return None
    @sampling_rate.setter
    def sampling_rate(self, value: int | float) -> None:
        if value == 500:
            self._sampling_rate = SamplingRate.HZ_500
            logger.info("Установлена частота HZ_500")
        if value == 1000:
            self._sampling_rate = SamplingRate.HZ_1000
            logger.info("Установлена частота HZ_1000")
        if value == 2000:
            self._sampling_rate = SamplingRate.HZ_2000
            logger.info("Установлена частота HZ_2000")

    async def activate(self, value: bool):
        """ активация устройства """
        if value:
            await self._setup(cmd=Command.Activate)

        if not value:
            await self._setup(cmd=Command.Deactivate)

        try:
            await self._read_device_status()
        except Exception as err:
            logger.error(f"Возникла ошибка чтения свойств {self.name}: err")

    async def _setup(self, cmd: Command, settings: Settings | bytes = b''):
        """ Установка команд и настроек inRat """
        data = cmd.to_bytes() + bytes(settings)
        data += get_control_sum(data, BLE_KEY)
        await self._client.write_gatt_char(inRat.UUID_CHARACTERISTIC_CONTROL, data)

    async def _read_property(self, characteristic: inRatCharacteristic) -> str:
        """ чтение свойств устройства"""
        rawdata = await self._client.read_gatt_char(str(characteristic))
        data = rawdata.decode()
        return data

    async def _read_device_properties(self) -> None:
        """ чтение свойств подключенного устройства """
        self._serial = await self._read_property(inRat.inRatCharacteristic.SERIAL)
        self._model = await self._read_property(inRat.inRatCharacteristic.MODEL)
        self._manufacturer = await self._read_property(inRat.inRatCharacteristic.MANUFACTURER_NAME)
        self._firmware = await self._read_property(inRat.inRatCharacteristic.FIRMWARE)
        self._hardware = await self._read_property(inRat.inRatCharacteristic.HARDWARE)
        logger.info(f"{self._name}; manufacturer: {self._manufacturer}; serial: {self._serial}; model: {self._model}; firmware: {self._firmware}; hardware: {self._firmware};")

    async def _read_device_status(self):
        """ чтение статуса устройства """
        rawbytes = await self._client.read_gatt_char(inRat.UUID_CHARACTERISTIC_STATUS)
        status = Status.from_buffer(rawbytes).to_dataclass()
        self._is_activated = status.activated
        logger.info(f"Прочитана структура Status: {status}")

    async def connect(self, wait: int = 10) -> bool:
        """ подключение к inRat """
        if self.is_connected:
            logger.warning("Устройство уже подключено!")
            return True

        res = True
        try:
            await asyncio.wait_for(self._client.connect(), timeout=wait)
            logger.info("Устройство подключено")

            try:
                await self._read_device_properties()
                await self._read_device_status()
            except Exception as err:
                logger.error(f"Ошибка во время получения статуса и свойств: {err}")
                await self.disconnect()
                res = False

        except asyncio.TimeoutError:
            logger.warning("Не удалось подключиться к устройству!")
            res = False
        except Exception as exc:
            logger.error(f"Возникла ошибка во время подключения к устройству! {exc}")
            res = False

        return res

    def _get_settings(self) -> Settings:
        """ генерация структуры настроек для запуска inRat на регистрацию данных """
        settings = Settings(
            DataRateEcg=self._sampling_rate, HighPassFilterEcg=self._high_pass_filter_ecg,
            FullScaleAccelerometer=self._full_scale_accelerometer, EnabledChannels=EnabledChannels.ECG,
            EnabledEvents=0, ActivityThreshold=1
        )
        return settings

    async def start_acquisition(self, data_queue: asyncio.Queue) -> bool:
        """ Запуск inRat на регистрацию сигнала и событий """
        async def event_handler(sender, data: bytearray):
            event_size = ctypes.sizeof(Event)
            cnt = int(len(data) / event_size)

            logger.debug(f"Получено событий: {cnt}")
            for idx in range(cnt):
                event = Event.from_buffer(data[idx: (idx + 1) * event_size])
                await data_queue.put({"type": "event", "counter": event.Counter, "event": event})

        async def signal_handler(sender, data: bytearray):
            time_received = time.time()
            cnt, sig = decode_ecg(data)
            await data_queue.put({"start_timestamp": start_timestamp, "type": "signal", "start_time": time_received, "counter": cnt, "signal": sig})

        settings = self._get_settings()
        try:
            start_timestamp = time.time()
            await self._setup(Command.AcquisitionStart, settings)
            await self._client.start_notify(self.UUID_CHARACTERISTIC_DATA_ECG, signal_handler)
            await self._client.start_notify(self.UUID_CHARACTERISTIC_EVENT, event_handler)
            self._is_notifying = True
        except Exception as err:
            logger.error(f"{err=}")
        return True

    async def stop_acquisition(self) -> None:
        """ Остановка inRat и отписка от сервисов """
        try:
            await self._client.stop_notify(self.UUID_CHARACTERISTIC_DATA_ECG)
        except Exception as exc:
            logger.debug(f"Возникла ошибка отписки от сервиса рассылки сигналов:\n{exc}")

        try:
            await self._client.stop_notify(self.UUID_CHARACTERISTIC_EVENT)
        except Exception as exc:
            logger.debug(f"Возникла ошибка отписки от сервиса рассылки событий:\n{exc}")

        try:
            await self._setup(Command.AcquisitionStop)
        except Exception as err:
            logger.debug(f"Возникла ошибка отписки от сервиса рассылки событий:\n{err}")

        self._is_notifying = False

    async def disconnect(self) -> bool:
        """ Отключение от устройства """
        if self._is_notifying:
            await self.stop_acquisition()

        try:
            await self._setup(Command.ConnectionClose)
        except Exception:
            ...

        try:
            await self._client.disconnect()
        except Exception:
            ...

        return True
