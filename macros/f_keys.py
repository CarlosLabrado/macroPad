# SPDX-FileCopyrightText: 2021 Emma Humphries for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Universal Numpad

from adafruit_hid.keycode import Keycode # REQUIRED if using Keycode.* values

app = {                # REQUIRED dict, must be named 'app'
    'name': 'F Keys',  # Application name
    'macros': [        # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x7F0000, 'F1', [Keycode.F1]),  # Very dim red
        (0x73000B, 'F2', [Keycode.F2]),
        (0x680017, 'F3', [Keycode.F3]),
        # 2nd row ----------
        (0x5C0022, 'F4', [Keycode.F4]),
        (0x51002E, 'F5', [Keycode.F5]),
        (0x450039, 'F6', [Keycode.F6]),
        # 3rd row ----------
        (0x390045, 'F7', [Keycode.F7]),
        (0x2E0051, 'F8', [Keycode.F8]),
        (0x22005C, 'F9', [Keycode.F9]),
        # 4th row ----------
        (0x170068, 'F10', [Keycode.F10]),
        (0x0B0073, 'F11', [Keycode.F11]),
        (0x00007F, 'F12', [Keycode.F12]), # Very dim green
        # Encoder button ---
        (0x000000, '', [Keycode.BACKSPACE])
    ]
}
