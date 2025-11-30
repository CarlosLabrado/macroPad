# SPDX-FileCopyrightText: 2024
# SPDX-License-Identifier: MIT

"""
Zoom/Video Meeting Controls for NeoKey 4-key pad.

Keys:
  0: Mute/Unmute (Alt+A in Zoom)
  1: Video On/Off (Alt+V in Zoom)
  2: Screen Share (Alt+S in Zoom)
  3: Leave Meeting (Alt+Q in Zoom)

Note: These shortcuts work in Zoom on Windows.
For Mac, change Keycode.ALT to Keycode.COMMAND.
"""

from adafruit_hid.keycode import Keycode

app = {
    "name": "Zoom",
    "macros": [
        # Key 0 - Mute/Unmute
        (0xFF0000, "Mute", [Keycode.ALT, Keycode.A]),

        # Key 1 - Video On/Off
        (0x0000FF, "Video", [Keycode.ALT, Keycode.V]),

        # Key 2 - Screen Share
        (0x00FF00, "Share", [Keycode.ALT, Keycode.S]),

        # Key 3 - Leave Meeting
        (0xFFFF00, "Leave", [Keycode.ALT, Keycode.Q]),
    ],
}
