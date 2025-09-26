import asyncio
import logging

from device.emgsens.constants import SamplingRate, ScaleGyro, Channel, ScaleAccel, EventType
from emgsens.emg_sens import EmgSens
from ble_scanner import find_device
from device.emgsens.structures import Settings

logger = logging.getLogger(__name__)

async def main():
    data_queue = asyncio.Queue()

    ble_device, _ = await find_device(timeout=10, template="EMG-SENS-1144")

    device = EmgSens(ble_device)
    await device.connect()

    st = Settings(
        DataRateEMG=SamplingRate.HZ_1000.value,
        AveragingWindowEMG=10,
        FullScaleAccelerometer=ScaleAccel.G_0.value,
        FullScaleGyroscope=ScaleGyro.DPS_125.value,
        EnabledChannels=Channel.eEMG|Channel.X|Channel.Y|Channel.Z|Channel.P|Channel.R|Channel.YAW,
        EnabledEvents=EventType.DISABLE,
        ActivityThreshold=1,
    )
    await device.get_data(data_queue=data_queue, settings=st)
    await asyncio.sleep(5)
    await device.disconnect()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())