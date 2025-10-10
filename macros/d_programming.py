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
    "name": "Code",  # Application name
    "macros": [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x99FF99, "Resume", [Keycode.F9]),  # Light green
        (0x88DD88, "Over", [Keycode.F8]),
        (0x77BB77, "Into", [Keycode.F7]),
        # 2nd row ----------
        (0x669966, "Run", [Keycode.LEFT_SHIFT, Keycode.F10]),
        (0x557755, "Debug", [Keycode.LEFT_SHIFT, Keycode.F9]),
        (0x446644, "Out", [Keycode.LEFT_SHIFT, Keycode.F8]),
        # 3rd row ----------
        (0x335533, "Usages", [Keycode.LEFT_ALT, Keycode.F7]),
        (0x224422, "Surnd", [Keycode.LEFT_CONTROL, Keycode.LEFT_ALT, Keycode.T]),
        (0x113311, "Refact", [Keycode.LEFT_SHIFT, Keycode.F6]),
        # 4th row ----------
        (0x556B2F, "Stop", [Keycode.LEFT_CONTROL, Keycode.F2]),  # Olive
        (0x556B2F, "Over", [Keycode.LEFT_CONTROL, Keycode.F2]),
        (0x556B2F, "Rerun", [Keycode.LEFT_CONTROL, Keycode.F5]),
        # Encoder button ---
        (0x000000, "", [Keycode.ESCAPE]),
    ],
}
