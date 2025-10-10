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
    "name": "Office",  # Application name
    "macros": [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (
            0x003366,
            "Screen",
            [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.S],
        ),  # Darker blue
        (0x003399, "RDPm", [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.HOME]),
        (0x0033CC, "CitrixM", [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.PAUSE]),
        # 2nd row ----------
        (0x0033FF, "HDR", [Keycode.GUI, Keycode.LEFT_ALT, Keycode.B]),  # Blue
        (
            0x0066FF,
            "Audio",
            [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.V],
        ),  # Light blue
        (
            0x0099FF,
            "Fancy",
            [Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.GRAVE_ACCENT],
        ),  # Lighter blue
        # 3rd row ----------
        (
            0x00CCFF,
            "Chat",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.J],
        ),
        (
            0x00FFFF,
            "FullS",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.F],
        ),  # Cyan, for variety
        (
            0x33FFFF,
            "Pause",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.G],
        ),
        # 4th row ----------
        (
            0x66FFFF,
            "Video",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.B],
        ),
        (
            0x99FFFF,
            "Share",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.S],
        ),
        (
            0xCCFFFF,
            "Mute",
            [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.LEFT_SHIFT, Keycode.A],
        ),  # Very light blue
        # Encoder button ---
        (0x000000, "", [Keycode.CAPS_LOCK]),
    ],
}
