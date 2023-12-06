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
    'name': 'Vash',  # Application name
    'macros': [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x00007F, 'SCShot', [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.S]),
        (0x0B0073, 'Crop', [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.T]),
        (0x170068, 'VFZ', [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.BACKSLASH]),
        # 2nd row ----------
        (0x22005C, 'HDR', [Keycode.GUI, Keycode.LEFT_ALT, Keycode.B]),
        (0x2E0051, 'SWAudio', [Keycode.GUI, Keycode.LEFT_CONTROL, Keycode.V]),
        (0x390045, 'Vol+', [[ConsumerControlCode.VOLUME_INCREMENT]]),
        # 3rd row ----------
        (0x450039, 'MainFZ', [Keycode.GUI, Keycode.LEFT_SHIFT, Keycode.GRAVE_ACCENT]),
        (0x51002E, 'Mute', [[ConsumerControlCode.MUTE]]),
        (0x5C0022, 'Vol-', [[ConsumerControlCode.VOLUME_DECREMENT]]),
        # 4th row ----------
        (0x680017, '<<', [[ConsumerControlCode.SCAN_PREVIOUS_TRACK]]),
        (0x73000B, 'Play/Pause', [[ConsumerControlCode.PLAY_PAUSE]]),
        (0x7F0000, '>>', [[ConsumerControlCode.SCAN_NEXT_TRACK]]),
        # Encoder button ---
        (0x000000, '', [Keycode.CAPS_LOCK])
    ]
}
