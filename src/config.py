import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class AppData:
    def __init__(self):
        self.app_dir = Path.home() / ".inRat planner"
        self.app_dir.mkdir(exist_ok=True)

        self.url_db = f"sqlite+pysqlite:///{self.app_dir}/InRat.db"
        self.path_to_data = self.app_dir / "data"
        self.preferences_file = self.app_dir / "config.ini"
        self.path_to_data.mkdir(exist_ok=True)

app_data = AppData()


def parse_ble_key(key: str):
    """
    Сonvert string to bytearray to interact with ble devices.
    :param key: str
    :return: bytearray
    """
    hex_str = key.strip()
    hex_values = [x.strip().replace("0x", "") for x in hex_str.split(",")]
    return bytearray([int(b, 16) for b in hex_values])


BLE_KEY_IN_RAT = parse_ble_key(os.getenv("INRAT"))
