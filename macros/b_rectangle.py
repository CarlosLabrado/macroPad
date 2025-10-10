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
    "name": "Rectangle",  # Application name
    "macros": [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x003366, "[ ]   ", [Keycode.ALT, Keycode.COMMAND, Keycode.LEFT_ARROW]),# Left half
        (0x00FFFF, "[      ]",  [Keycode.ALT, Keycode.COMMAND, Keycode.ENTER]),# Full screen
        (0x0033CC, "   [ ]", [Keycode.ALT, Keycode.COMMAND, Keycode.RIGHT_ARROW]),# Right half
        # 2nd row ----------
        (0x00CCFF, "[]   ",   [Keycode.ALT, Keycode.COMMAND, Keycode.Y]),# Left fourth
        (0x003399, "[   ]", [Keycode.ALT, Keycode.COMMAND, Keycode.P]),# Mid Half
        (0x33FFFF, "   []",  [Keycode.ALT, Keycode.COMMAND, Keycode.N]),# Right fourth
        # 3rd row ----------
        (0x66FFFF, "[ ]  ", [Keycode.ALT, Keycode.COMMAND, Keycode.D]),# Left third
        (0x99FFFF, " [ ] ", [Keycode.ALT, Keycode.COMMAND, Keycode.F]),# Mid third
        (0xCCFFFF, "  [ ]", [Keycode.ALT, Keycode.COMMAND, Keycode.G]),# Right third
        # 4th row ----------
        (0x680017, "<<", [[ConsumerControlCode.SCAN_PREVIOUS_TRACK]]),
        (0x73000B, "Play", [[ConsumerControlCode.PLAY_PAUSE]]),
        (0x7F0000, ">>", [[ConsumerControlCode.SCAN_NEXT_TRACK]]),
        # Encoder button ---
        (0x000000, "", [Keycode.CAPS_LOCK]),
    ],
}