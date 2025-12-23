import os

from dotenv import load_dotenv

load_dotenv()

def parse_ble_key(key: str):
    """
    Сonvert string to bytearray to interact with ble devices.
    :param key: str
    :return: bytearray
    """
    hex_str = key.strip()
    hex_values = [x.strip().replace("0x", "") for x in hex_str.split(",")]
    return bytearray([int(b, 16) for b in hex_values])


BLE_KEY_EMGSENS = parse_ble_key(os.getenv('BLE_KEY_EMG_SENS'))
BLE_KEY_IN_RAT = parse_ble_key(os.getenv('BLE_KEY_IN_RAT'))
DB_PATH = os.getenv('DB_PATH')
DB_NAME = os.getenv('DB_NAME')
SAVE_DIR = os.getenv("SAVE_DIR")
PATH_TO_ICON = os.getenv("PATH_TO_ICON")
PATH_TO_ICON_MCS = os.getenv("PATH_TO_ICON_MCS")
PATH_TO_LICENSES = os.getenv("PATH_TO_LICENSES")

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)