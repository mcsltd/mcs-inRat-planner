import logging

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        pass

    def start_recording(self, serial_number, start_time, duration):
        logger.debug(f"Start task: {start_time=} with {duration=} for device with {serial_number=}")