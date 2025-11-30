# SPDX-FileCopyrightText: 2024 Adapted for LED Glasses Driver + NeoKey 1x4
# SPDX-License-Identifier: MIT

"""
A 4-key macro pad using Adafruit LED Glasses Driver nRF52840 + NeoKey 1x4 QT.

Connect NeoKey 1x4 to the LED Glasses Driver via STEMMA QT cable.
Requires CircuitPython 10.x with USB HID enabled.

Features:
- 4 programmable mechanical keys with NeoPixels
- USB HID keyboard and consumer control
- Configurable macros via /macros_4key folder
- Auto-reconnection on I2C errors
"""

import os
import time
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from micropython import const
from adafruit_seesaw import neopixel
from adafruit_seesaw.seesaw import Seesaw

# CONFIGURABLES ------------------------
MACRO_FOLDER = "/macros_4key"
INITIAL_BRIGHTNESS = 0.1
NEOKEY_ADDR = 0x30
NEOKEY_RECONNECT_INTERVAL = 5.0

# NeoKey1x4 Constants
_NEOKEY1X4_NEOPIX_PIN = const(3)
_NEOKEY1X4_NUM_KEYS = const(4)

# Default key colors (can be overridden by macros)
DEFAULT_COLORS = [0x00FF00, 0x0000FF, 0xFF0000, 0xFFFF00]  # Green, Blue, Red, Yellow
PRESSED_COLOR = 0x800080  # Purple when pressed


class NeoKey1x4(Seesaw):
    """Driver for the Adafruit NeoKey 1x4."""

    def __init__(self, i2c_bus, addr=NEOKEY_ADDR, brightness=0.1):
        super().__init__(i2c_bus, addr)
        self.pixels = neopixel.NeoPixel(
            self,
            _NEOKEY1X4_NEOPIX_PIN,
            _NEOKEY1X4_NUM_KEYS,
            brightness=brightness,
            pixel_order=neopixel.GRB,
        )
        # Set pins 4-7 to inputs with pullups
        for b in range(4, 8):
            self.pin_mode(b, self.INPUT_PULLUP)

    def __getitem__(self, index):
        """Read a single key state."""
        if not isinstance(index, int) or index < 0 or index > 3:
            raise RuntimeError("Index must be 0 thru 3")
        return not self.digital_read(index + 4)

    def get_keys(self):
        """Read all 4 keys at once."""
        bulk_read = self.digital_read_bulk(0xF0)
        return [bulk_read & (1 << i) == 0 for i in range(4, 8)]


class NeoKeyManager:
    """Manages NeoKey1x4 connection with automatic reconnection."""

    def __init__(self, i2c_bus, addr=NEOKEY_ADDR, brightness=0.1):
        self.i2c_bus = i2c_bus
        self.addr = addr
        self.brightness = brightness
        self.device = None
        self.is_connected = False
        self._last_reconnect = 0
        self._failed_reads = 0
        self._connect()

    def _connect(self):
        """Attempt to connect to the NeoKey device."""
        try:
            self.device = NeoKey1x4(
                self.i2c_bus, addr=self.addr, brightness=self.brightness
            )
            self.is_connected = True
            self._failed_reads = 0
            print(f"NeoKey connected at {hex(self.addr)}")
            return True
        except (OSError, RuntimeError, ValueError) as e:
            self.is_connected = False
            self.device = None
            print(f"NeoKey connection failed: {e}")
            return False

    def _try_reconnect(self):
        """Attempt reconnection with rate limiting."""
        current_time = time.monotonic()
        if current_time - self._last_reconnect >= NEOKEY_RECONNECT_INTERVAL:
            self._last_reconnect = current_time
            print("Attempting NeoKey reconnection...")
            self._connect()

    def get_keys(self):
        """Safely read all key states."""
        if not self.is_connected:
            self._try_reconnect()
            return [False, False, False, False]

        try:
            keys = self.device.get_keys()
            self._failed_reads = 0
            return keys
        except (OSError, RuntimeError, ValueError) as e:
            self._failed_reads += 1
            if self._failed_reads >= 3:
                print(f"NeoKey read failed, marking disconnected: {e}")
                self.is_connected = False
            return [False, False, False, False]

    def set_pixel(self, index, color):
        """Safely set a pixel color."""
        if not self.is_connected or not self.device:
            return
        try:
            self.device.pixels[index] = color
        except (OSError, RuntimeError, ValueError):
            pass

    def set_all_pixels(self, colors):
        """Set all pixel colors at once."""
        if not self.is_connected or not self.device:
            return
        try:
            for i, color in enumerate(colors):
                self.device.pixels[i] = color
        except (OSError, RuntimeError, ValueError):
            pass

    def set_brightness(self, brightness):
        """Safely set brightness."""
        self.brightness = brightness
        if self.is_connected and self.device:
            try:
                self.device.pixels.brightness = brightness
            except (OSError, RuntimeError, ValueError):
                pass


class Debouncer:
    """Simple button debouncer."""

    def __init__(self):
        self.state = False
        self.last_state = False

    def update(self, new_state):
        """Update debouncer state."""
        self.last_state = self.state
        self.state = new_state

    def is_pressed(self):
        """Check if button was just pressed (rising edge)."""
        return self.state and not self.last_state

    def is_released(self):
        """Check if button was just released (falling edge)."""
        return not self.state and self.last_state


def load_macros(macro_folder):
    """Load macro configuration from folder.

    Returns:
        Dictionary with 'name' and 'macros' list, or default config.
    """
    try:
        files = os.listdir(macro_folder)
        files.sort()

        for filename in files:
            if filename.endswith(".py") and not filename.startswith("._"):
                try:
                    module = __import__(macro_folder + "/" + filename[:-3])
                    print(f"Loaded macros from {filename}")
                    return module.app
                except (SyntaxError, ImportError, AttributeError, KeyError) as err:
                    print(f"ERROR loading {filename}: {err}")
    except OSError:
        print(f"Macro folder {macro_folder} not found, using defaults")

    # Default macros if no file found
    return {
        "name": "Default",
        "macros": [
            (0x00FF00, "Esc", [Keycode.ESCAPE]),
            (0x0000FF, "Vol+", [[ConsumerControlCode.VOLUME_INCREMENT]]),
            (0xFF0000, "Vol-", [[ConsumerControlCode.VOLUME_DECREMENT]]),
            (0xFFFF00, "Play", [[ConsumerControlCode.PLAY_PAUSE]]),
        ],
    }


def execute_macro(sequence, pressed, keyboard, kbd_layout, consumer_control):
    """Execute a macro key sequence.

    Args:
        sequence: List of macro actions (keycodes, delays, strings, lists).
        pressed: True if key pressed, False if released.
        keyboard: Keyboard HID instance.
        kbd_layout: KeyboardLayoutUS instance.
        consumer_control: ConsumerControl HID instance.
    """
    if pressed:
        for item in sequence:
            if isinstance(item, int):
                # Keycode: positive = press, negative = release
                if item >= 0:
                    keyboard.press(item)
                else:
                    keyboard.release(-item)
            elif isinstance(item, float):
                # Delay
                time.sleep(item)
            elif isinstance(item, str):
                # Type string
                kbd_layout.write(item)
            elif isinstance(item, list):
                # Consumer control codes (media keys)
                for code in item:
                    if isinstance(code, int):
                        consumer_control.release()
                        consumer_control.press(code)
                        time.sleep(0.1)
                    elif isinstance(code, float):
                        time.sleep(code)
    else:
        # Release all on key up
        for item in sequence:
            if isinstance(item, int) and item >= 0:
                keyboard.release(item)
        consumer_control.release()


# INITIALIZATION -----------------------

print("\n" + "=" * 40)
print("NeoKey 4-Key Macro Pad")
print("LED Glasses Driver nRF52840")
print("=" * 40)

# Initialize USB HID
print("Initializing USB HID...")
keyboard = Keyboard(usb_hid.devices)
kbd_layout = KeyboardLayoutUS(keyboard)
consumer_control = ConsumerControl(usb_hid.devices)

# Initialize I2C and NeoKey
print("Initializing NeoKey 1x4...")
try:
    i2c_bus = board.I2C()
    neokey = NeoKeyManager(i2c_bus, brightness=INITIAL_BRIGHTNESS)
except Exception as e:
    print(f"Failed to initialize I2C: {e}")
    print("Check STEMMA QT connection!")
    # Flash onboard LED if available to indicate error
    while True:
        time.sleep(1)

# Load macros
print("Loading macros...")
app = load_macros(MACRO_FOLDER)
macros = app["macros"]

# Initialize state
debouncers = [Debouncer() for _ in range(4)]
key_colors = [macro[0] for macro in macros]

# Set initial LED colors
neokey.set_all_pixels(key_colors)

print(f"Loaded: {app['name']}")
print("Keys configured:")
for i, macro in enumerate(macros):
    print(f"  Key {i}: {macro[1]}")
print("=" * 40)
print("Ready!\n")

# MAIN LOOP ----------------------------

while True:
    # Read key states
    keys = neokey.get_keys()

    for i in range(4):
        debouncers[i].update(keys[i])

        if debouncers[i].is_pressed():
            # Key just pressed
            print(f"Key {i} pressed: {macros[i][1]}")
            neokey.set_pixel(i, PRESSED_COLOR)

            sequence = macros[i][2]
            execute_macro(sequence, True, keyboard, kbd_layout, consumer_control)

        elif debouncers[i].is_released():
            # Key just released
            neokey.set_pixel(i, key_colors[i])

            sequence = macros[i][2]
            execute_macro(sequence, False, keyboard, kbd_layout, consumer_control)

    # Small delay to prevent CPU hogging
    time.sleep(0.01)
