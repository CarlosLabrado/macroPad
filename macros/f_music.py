# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# MACROPAD Hotkeys example: Consumer Control codes (media keys)

# The syntax for Consumer Control macros is a little peculiar, in order to
# maintain backward compatibility with the original keycode-only macro files.
# The third item for each macro is a list in brackets, and each value within
# is normally an integer (Keycode), float (delay) or string (typed literally).
# Consumer Control codes are distinguished by enclosing them in a list within
# the list, which is why you'll see double brackets [[ ]] below.
# Like Keycodes, Consumer Control codes can be positive (press) or negative
# (release), and float values can be inserted for pauses.

# To reference Consumer Control codes, import ConsumerControlCode like so...
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keycode import Keycode  # REQUIRED if using Keycode.* values

app = {  # REQUIRED dict, must be named 'app'
    "name": "YouTube Music",  # Application name
    "macros": [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x00007F, "Screen", [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.S]),
        (
            0x0B0073,
            "WIN",
            [Keycode.GUI],
        ),
        (0x170068, "VFZ", [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.BACKSLASH]),
        # 2nd row ----------
        (0x22005C, "Up", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F7]),
        (0x2E0051, "Audio", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.V]),
        (0x390045, "Vol+", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F6]),
        # 3rd row ----------
        (0x51002E, "Down", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F5]),
        (0x51002E, "Mute", [[ConsumerControlCode.MUTE]]),
        (0x51002E, "Vol-", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F4]),
        # 4th row ----------
        (0x51002E, "<<", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F3]),
        (0x51002E, "Play", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F2]),
        (0x51002E, ">>", [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.F1]),
        # Encoder button ---
        (0x000000, "", [Keycode.CAPS_LOCK]),
    ],
}
