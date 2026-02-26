import asyncio
import contextlib
import ctypes
import hashlib
import logging
import time

from bleak import BLEDevice, BleakClient, BleakScanner, BleakError
from asyncio import Queue
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

from src.config import BLE_KEY_IN_RAT
from src.device.inrat_v1.decoder import decode_ecg
from src.device.inrat_v1.enums import Command, EnabledChannels, EventType, SamplingRate, ScaleAccelerometer
from src.device.inrat_v1.structures import Settings, Event

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

    def __init__(self, ble_device: BLEDevice):
        self._client: BleakClient = BleakClient(ble_device)

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    async def _setup(self, cmd: Command, settings: Settings | bytes = b''):
        """ Установка команд и настроек inRat """
        data = cmd.to_bytes() + bytes(settings)
        data += get_control_sum(data, BLE_KEY)
        await self._client.write_gatt_char(inRat.UUID_CHARACTERISTIC_CONTROL, data)

    async def connect(self, wait: int = 10) -> bool:
        """ Подключение к inRat """
        res = True
        if self.is_connected:
            logger.warning("Устройство уже подключено!")
            return res

        try:
            await asyncio.wait_for(self._client.connect(), timeout=wait)
            logger.info("Устройство подключено")

        except asyncio.TimeoutError:
            logger.warning("Не удалось подключиться к устройству!")
            res = False
        except Exception as exc:
            logger.error(f"Возникла ошибка во время подключения к устройству! {exc}")
            res = False

        return res

    async def start_acquisition(self, qsignal: Queue | None = None, qevent: Queue | None = None) -> None:
        """ Запуск inRat на регистрацию сигнала и событий """
        async def event_handler(sender, data: bytearray):
            event_size = ctypes.sizeof(Event)
            cnt = int(len(data) / event_size)

            logger.debug(f"Получено событий: {cnt}")
            for idx in range(cnt):
                event = Event.from_buffer(data[idx: (idx + 1) * event_size])
                await qevent.put({"counter": event.Counter, "event": event})

        async def signal_handler(sender, data: bytearray):
            cnt, sig = decode_ecg(data)
            await qsignal.put({"counter": cnt, "signal": sig})

        settings = Settings(
            DataRateEcg=SamplingRate.HZ_500,
            HighPassFilterEcg=0,
            FullScaleAccelerometer=ScaleAccelerometer.G_2,
            EnabledChannels=EnabledChannels.ECG,
            EnabledEvents=EventType.BUTTON | EventType.ACTIVITY | EventType.FREEFALL | EventType.ORIENTATION | EventType.START | EventType.TEMP,
            ActivityThreshold=1
        )

        await self._setup(Command.AcquisitionStart, settings)
        if qsignal:
            await self._client.start_notify(self.UUID_CHARACTERISTIC_DATA_ECG, signal_handler)
        if qevent:
            await self._client.start_notify(self.UUID_CHARACTERISTIC_EVENT, event_handler)


    async def stop_acquisition(self) -> None:
        """ Запуск inRat на регистрацию сигнала и событий """
        try:
            await self._client.stop_notify(self.UUID_CHARACTERISTIC_DATA_ECG)
        except Exception as exc:
            logger.debug(f"Возникла ошибка описки от сервиса рассылки сигналов:\n{exc}")

        try:
            await self._client.stop_notify(self.UUID_CHARACTERISTIC_EVENT)
        except Exception as exc:
            logger.debug(f"Возникла ошибка описки от сервиса рассылки событий:\n{exc}")

        await self._setup(Command.AcquisitionStop)

    async def disconnect(self) -> bool:
        """ Отключение от устройства """
        await self._setup(Command.AcquisitionStop)
        await self._client.disconnect()


async def main():
    device = await BleakScanner.find_device_by_name(name="inRat-1-1022")

    device = inRat(device)
    if await device.connect():
        queue_signal, queue_event = Queue(maxsize=50), Queue(maxsize=50)
        await device.start_acquisition(queue_signal, queue_event)
        await asyncio.sleep(30)
        await device.stop_acquisition()
        await device.disconnect()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())