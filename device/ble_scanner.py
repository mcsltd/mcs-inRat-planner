import asyncio
import contextlib
import logging

from bleak import BLEDevice, AdvertisementData, BleakScanner

logger = logging.getLogger(__name__)

async def find_device(
        timeout: int | None = None,
        template: str = "EMG-SENS",
) -> tuple[BLEDevice, AdvertisementData] | tuple[None, None]:
    """
    Find ble device on template.
    """
    async with BleakScanner() as scanner:
        with contextlib.suppress(asyncio.TimeoutError):
            async with asyncio.timeout(timeout):
                async for device, advertisement in scanner.advertisement_data():
                    if device is not None and device.name is not None and device.name.startswith(template):
                        return device, advertisement
    return None, None


async def main():
    print(await find_device(timeout=10))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())