from PySide6.QtBluetooth import QBluetoothLocalDevice


def is_bluetooth_enabled():
    """ Проверка включения bluetooth-адаптера """
    if QBluetoothLocalDevice().hostMode() == QBluetoothLocalDevice.HostMode.HostPoweredOff:
        return False
    return True

if __name__ == "__main__":
    print(is_bluetooth_enabled())
