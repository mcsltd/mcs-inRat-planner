import numpy as np
import struct

from typing import Tuple

from constants import Pkt, Constants
from structures import Settings


class Decoder:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.prevs = [0] * Pkt.ChannelsCountData

    def decode_data(self, raw_data: bytearray) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray]:
        offset = 2

        e_emg = np.zeros((1, Pkt.SamplesCountData))
        accel = np.zeros((3, Pkt.SamplesCountData))
        gyro = np.zeros((3, Pkt.SamplesCountData))

        counter = struct.unpack('<H', raw_data[:offset])[0]

        for idx_sample in range(Pkt.SamplesCountData):  # 8 samples
            code = raw_data[offset]
            offset += 1

            for ch in range(Pkt.ChannelsCountData):  # 7 channels - new countdown

                if (self.settings.EnabledChannels >> (ch + 1)) & 0x1 == 1:
                    if (code >> ch) & 0x1 == 0x0:
                        val = self.prevs[ch] + int.from_bytes([raw_data[offset]], byteorder='little', signed=True)
                        offset += 1

                    if (code >> ch) & 0x1 == 0x1:
                        val = int.from_bytes(raw_data[offset:offset + 2], byteorder='little', signed=True)
                        offset += 2

                    self.prevs[ch] = val

                    # get eemg
                    if ch == 0:
                        e_emg[ch][idx_sample] = val
                    # get acceleration
                    elif 1 <= ch <= 3:
                        accel[ch - 1][idx_sample] = val
                    # get gyro
                    elif 4 <= ch <= 6:
                        gyro[ch - 4][idx_sample] = val

        e_emg *= Constants.EmgResolution
        accel *= Constants.AccResolution * (2 ** self.settings.FullScaleAccelerometer)
        gyro *= Constants.GyroResolution * (2 ** self.settings.FullScaleGyroscope)

        return counter, e_emg, accel, gyro