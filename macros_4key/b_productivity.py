# SPDX-FileCopyrightText: 2024
# SPDX-License-Identifier: MIT

"""
Productivity Shortcuts for NeoKey 4-key pad.

Keys:
  0: Copy (Ctrl+C)
  1: Paste (Ctrl+V)
  2: Undo (Ctrl+Z)
  3: Save (Ctrl+S)
"""

from adafruit_hid.keycode import Keycode

app = {
    "name": "Productivity",
    "macros": [
        # Key 0 - Copy
        (0x00FFFF, "Copy", [Keycode.CONTROL, Keycode.C]),

        # Key 1 - Paste
        (0xFF00FF, "Paste", [Keycode.CONTROL, Keycode.V]),

        # Key 2 - Undo
        (0xFFA500, "Undo", [Keycode.CONTROL, Keycode.Z]),

        # Key 3 - Save
        (0x00FF00, "Save", [Keycode.CONTROL, Keycode.S]),
    ],
}
