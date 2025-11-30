# SPDX-FileCopyrightText: 2024
# SPDX-License-Identifier: MIT

"""
Media Controls - Default macro set for NeoKey 4-key pad.

Keys:
  0: Escape (green)
  1: Volume Up (blue)
  2: Volume Down (red)
  3: Play/Pause (yellow)
"""

from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

app = {
    "name": "Media",
    "macros": [
        # Key 0 - Escape
        (0x00FF00, "Esc", [Keycode.ESCAPE]),

        # Key 1 - Volume Up
        (0x0000FF, "Vol+", [[ConsumerControlCode.VOLUME_INCREMENT]]),

        # Key 2 - Volume Down
        (0xFF0000, "Vol-", [[ConsumerControlCode.VOLUME_DECREMENT]]),

        # Key 3 - Play/Pause
        (0xFFFF00, "Play", [[ConsumerControlCode.PLAY_PAUSE]]),
    ],
}
