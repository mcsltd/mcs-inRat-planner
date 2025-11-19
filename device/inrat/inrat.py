import asyncio
import logging
import time
from enum import Enum

from bleak import BleakClient, BLEDevice, BleakScanner

from config import BLE_KEY_IN_RAT
# from constants import ConnectionState
from device.crypt import get_control_sum
from device.inrat.constants import Command, DataRateEcg, ScaleAccelerometer, EnabledChannels, EventType
from device.inrat.decoder import Decoder
from device.inrat.structures import Settings

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """ Класс, описывающий состояния подключений к EmgSens """
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"


class InRat:

    UUID_ACQUISITION_SERVICE = "59573ef1-5389-575f-87d5-5f31fcdcba7b"
    UUID_EVENT_SERVICE = "f553739f-9f1f-538d-a7d3-cd987b395eb5"
    UUID_CHARACTERISTIC_CONTROL = "7395ca15-5997-5a1b-a138-75a7a573b8e5"

    def __init__(self, ble_device: BLEDevice):
        if ble_device is None:
            raise ValueError("BLEDevice не может быть None")

        self._client: BleakClient = BleakClient(ble_device)
        self._connection_state = ConnectionState.DISCONNECTED
        self._is_notifying = False

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected

    async def connect(self, timeout: float) -> bool:
        """ Подключение к устройству с таймаутом """
        if self.is_connected:
            return True

        self._connection_state = ConnectionState.CONNECTING
        try:
            await asyncio.wait_for(self._client.connect(), timeout=timeout)
            self._connection_state = ConnectionState.CONNECTED
        except asyncio.TimeoutError:
            self._connection_state = ConnectionState.DISCONNECTED
            return False
        except Exception as exp:
            self._connection_state = ConnectionState.DISCONNECTED
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
        except Exception as exp:
            return
        finally:
            self._connection_state = ConnectionState.DISCONNECTED

    async def stop_acquisition(self) -> bool:
        """ Остановка получения данных """
        if not self._is_notifying:
            return True

        try:
            if self.is_connected:
                try:
                    await self._client.stop_notify(self.UUID_ACQUISITION_SERVICE)
                except Exception as exc:
                    pass

                try:
                    await self._client.stop_notify(self.UUID_EVENT_SERVICE)
                except Exception as exc:
                    pass

            self._is_notifying = False

        except Exception as exp:
            return False
        return True

    async def setup(self, cmd: Command, settings: Settings = b'') -> bool:
        if not self.is_connected:
            return False

        try:
            data = cmd.value.to_bytes() + bytes(settings)
            data += get_control_sum(data=data, key=BLE_KEY_IN_RAT)
            await self._client.write_gatt_char(
                self.UUID_CHARACTERISTIC_CONTROL,
                data, response=True
            )
            return True
        except Exception as exp:
            return False

    async def start_signal_acquisition(self, signal_queue: asyncio.Queue, settings: Settings):
        if self._is_notifying:
            return False

        async def signal_handler(_, raw_data: bytearray):
            try:
                sample_timestamp = time.time()
                counter, signal = decoder.decode_signal(raw_data)

                await signal_queue.put({"counter": counter, "signal": signal,
                                        "timestamp": sample_timestamp, "start_timestamp": start_timestamp})
            except Exception as exp:
                pass

        try:
            success = await self.setup(cmd=Command.AcquisitionStart, settings=settings)
            if not success:
                return False
            start_timestamp = time.time()
            decoder = Decoder()
            await self._client.start_notify(self.UUID_ACQUISITION_SERVICE, signal_handler)
            self._is_notifying = True
            return True

        except Exception as exp:
            return False

    # async def start_event_acquisition(self, event_queue: asyncio.Queue, settings: Settings):
    #     if self._is_notifying:
    #         return False
    #
    #     async def event_handler(_, raw_data: bytearray):
    #         ...
    #
    #     try:
    #         success = await self.setup(cmd=Command., settings=settings)
    #         if not success:
    #             return False
    #
    #         start_timestamp = time.time()
    #         decoder = Decoder()
    #
    #         await self._client.start_notify(self.UUID_EVENT_SERVICE, event_handler)
    #         self._is_notifying = True
    #         return True
    #
    #     except Exception as exp:
    #         return False

async def start():

    ble_device = await BleakScanner.find_device_by_name(name="inRat-1-1016")
    inrat = InRat(ble_device)
    print(f"{inrat=}")
    if await inrat.connect(timeout=10):
        queue = asyncio.Queue()
        await inrat.start_signal_acquisition(
            signal_queue=queue,
            settings=Settings(
                DataRateEcg=DataRateEcg.HZ_500.value,
                HighPassFilterEcg=0,
                FullScaleAccelerometer=ScaleAccelerometer.G_2.value,
                EnabledChannels=EnabledChannels.ECG,
                EnabledEvents=EventType.START | EventType.TEMP,
                ActivityThreshold=1,
            )
        )
        await asyncio.sleep(10)
        await inrat.stop_acquisition()
        await inrat.disconnect()

        print(queue)
        _ = 1
    else:
        print("not connected")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(start())