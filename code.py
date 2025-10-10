# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
A macro/hotkey program for Adafruit MACROPAD with NeoKey1x4 extension.

Macro setups are stored in the /macros folder. Use the dial to select an
application macro set, press MACROPAD keys to send key sequences.

Features:
- Automatic sleep/wake for display and LEDs
- Brightness control via macros
- Resilient NeoKey1x4 connection with auto-reconnection
- Scrolling application name display
"""

# pylint: disable=import-error, unused-import, too-few-public-methods

import os
import time
import displayio
import terminalio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad
import board
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from micropython import const
from adafruit_seesaw import neopixel
from adafruit_seesaw.seesaw import Seesaw

try:
    import typing
    from busio import I2C
except ImportError:
    pass

# CONFIGURABLES ------------------------
MACRO_FOLDER = "/macros"
INITIAL_BRIGHTNESS = 0.1
SLEEP_TIME = 60 * 60  # 1 hour in seconds
NEOKEY_ADDR = 0x30
NEOKEY_RECONNECT_INTERVAL = 5.0

# NeoKey1x4 Constants
_NEOKEY1X4_NEOPIX_PIN = const(3)
_NEOKEY1X4_NUM_KEYS = const(4)


class NeoKey1x4(Seesaw):
    """Driver for the Adafruit NeoKey 1x4.

    Args:
        i2c_bus: I2C bus instance.
        interrupt: Enable interrupt mode. Default is False.
        addr: I2C address. Default is 0x30.
        brightness: NeoPixel brightness (0.0-1.0). Default is 0.01.
    """

    def __init__(
            self,
            i2c_bus: I2C,
            interrupt: bool = False,
            addr: int = NEOKEY_ADDR,
            brightness: float = 0.01,
    ) -> None:
        super().__init__(i2c_bus, addr)
        self.interrupt_enabled = interrupt
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

    def __getitem__(self, index: int) -> bool:
        """Read a single key state.

        Args:
            index: Key index (0-3).

        Returns:
            True if key is pressed, False otherwise.

        Raises:
            RuntimeError: If index is out of range.
        """
        if not isinstance(index, int) or (index < 0) or (index > 3):
            raise RuntimeError("Index must be 0 thru 3")
        return not self.digital_read(index + 4)

    def get_keys(self) -> typing.List[bool]:
        """Read all 4 keys at once.

        Returns:
            List of 4 boolean values, one per key.
        """
        bulk_read = self.digital_read_bulk(0xF0)
        keys = [bulk_read & (1 << i) == 0 for i in range(4, 8)]
        return keys


class NeoKeyManager:
    """Manages NeoKey1x4 connection with automatic reconnection.

    Attributes:
        i2c_bus: I2C bus instance.
        addr: I2C address of the NeoKey.
        brightness: Current brightness level.
        is_connected: Connection status.
    """

    def __init__(self, i2c_bus, addr=NEOKEY_ADDR, brightness=0.01):
        """Initialize NeoKey manager.

        Args:
            i2c_bus: I2C bus instance from board.I2C().
            addr: I2C address. Default is 0x30.
            brightness: Initial brightness. Default is 0.01.
        """
        self.i2c_bus = i2c_bus
        self.addr = addr
        self.brightness = brightness
        self.device = None
        self.is_connected = False
        self._last_reconnect = 0
        self._failed_reads = 0

        self._connect()

    def _connect(self):
        """Attempt to connect to the NeoKey device.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.device = NeoKey1x4(self.i2c_bus, addr=self.addr, brightness=self.brightness)
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
        current_time = time.time()
        if current_time - self._last_reconnect >= NEOKEY_RECONNECT_INTERVAL:
            self._last_reconnect = current_time
            print("Attempting NeoKey reconnection...")
            self._connect()

    def get_keys(self):
        """Safely read all key states.

        Returns:
            List of 4 boolean values, or all False if disconnected.
        """
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
        """Safely set a pixel color.

        Args:
            index: Pixel index (0-3).
            color: RGB color as integer (0xRRGGBB).
        """
        if not self.is_connected or not self.device:
            return

        try:
            self.device.pixels[index] = color
        except (OSError, RuntimeError, ValueError):
            pass  # Silently fail for LED operations

    def set_brightness(self, brightness):
        """Safely set brightness.

        Args:
            brightness: Brightness level (0.0-1.0).
        """
        self.brightness = brightness
        if self.is_connected and self.device:
            try:
                self.device.pixels.brightness = brightness
            except (OSError, RuntimeError, ValueError):
                pass


class Debouncer:
    """Simple button debouncer.

    Attributes:
        state: Current button state.
        last_state: Previous button state.
    """

    def __init__(self):
        """Initialize debouncer with False state."""
        self.state = False
        self.last_state = False

    def update(self, new_state):
        """Update debouncer state.

        Args:
            new_state: New button state.
        """
        self.last_state = self.state
        self.state = new_state

    def is_pressed(self):
        """Check if button was just pressed.

        Returns:
            True if button transitioned from not pressed to pressed.
        """
        return self.state and not self.last_state


class DisplayManager:
    """Manages display sleep/wake and brightness.

    Attributes:
        brightness: Current brightness level (0.0-1.0).
        is_asleep: Whether display is currently asleep.
    """

    def __init__(self, initial_brightness):
        """Initialize display manager.

        Args:
            initial_brightness: Starting brightness (0.0-1.0).
        """
        self.brightness = initial_brightness
        self.is_asleep = False

    def wake_display(self, macropad, neokey_manager=None):
        """Wake the display and restore brightness.

        Args:
            macropad: MacroPad instance.
            neokey_manager: Optional NeoKeyManager instance.

        Returns:
            Current time as float.
        """
        if self.is_asleep:
            print("Waking display")
            macropad.display_sleep = False
            macropad.pixels.brightness = self.brightness
            macropad.pixels.show()
            macropad.display.refresh()
            self.is_asleep = False

            if neokey_manager:
                neokey_manager.set_brightness(self.brightness)
                if not neokey_manager.is_connected:
                    neokey_manager._try_reconnect()

        return time.time()

    def sleep_display(self, macropad, neokey_manager=None):
        """Put display to sleep and turn off LEDs.

        Args:
            macropad: MacroPad instance.
            neokey_manager: Optional NeoKeyManager instance.
        """
        if not self.is_asleep:
            print("Sleeping display")
            macropad.display_sleep = True
            macropad.pixels.brightness = 0.0
            macropad.pixels.show()
            macropad.display.refresh()
            self.is_asleep = True

            if neokey_manager:
                neokey_manager.set_brightness(0.0)

    def manage_sleep(self, start_time, sleep_timeout, macropad, neokey_manager=None):
        """Check and manage sleep state based on inactivity.

        Args:
            start_time: Timestamp of last activity.
            sleep_timeout: Seconds of inactivity before sleep.
            macropad: MacroPad instance.
            neokey_manager: Optional NeoKeyManager instance.
        """
        elapsed = time.time() - start_time
        if elapsed >= sleep_timeout and not self.is_asleep:
            self.sleep_display(macropad, neokey_manager)

    def adjust_brightness(self, delta, macropad, neokey_manager=None):
        """Adjust brightness up or down.

        Args:
            delta: Amount to change brightness (can be negative).
            macropad: MacroPad instance.
            neokey_manager: Optional NeoKeyManager instance.

        Returns:
            New brightness value.
        """
        self.brightness = max(0.0, min(1.0, self.brightness + delta))
        print(f"Brightness: {self.brightness:.2f}")

        macropad.pixels.brightness = self.brightness
        macropad.pixels.show()

        if neokey_manager:
            neokey_manager.set_brightness(self.brightness)

        return self.brightness


class App:
    """Represents a macro application with key bindings.

    Attributes:
        name: Application name displayed on screen.
        macros: List of macro definitions for each key.
    """

    def __init__(self, appdata):
        """Initialize App from macro file data.

        Args:
            appdata: Dictionary with 'name' and 'macros' keys.
        """
        self.name = appdata["name"]
        self.macros = appdata["macros"]

    def switch(self, macropad, group):
        """Switch to this application.

        Updates display labels and LED colors for all keys.

        Args:
            macropad: MacroPad instance.
            group: DisplayIO group for labels.
        """
        group[13].text = self.name

        for i in range(12):
            if i < len(self.macros):
                macropad.pixels[i] = self.macros[i][0]
                group[i].text = self.macros[i][1]
            else:
                macropad.pixels[i] = 0
                group[i].text = ""

        macropad.keyboard.release_all()
        macropad.consumer_control.release()
        macropad.mouse.release_all()
        macropad.stop_tone()
        macropad.pixels.show()
        macropad.display.refresh()


def load_apps(macro_folder):
    """Load all macro applications from folder.

    Args:
        macro_folder: Path to folder containing .py macro files.

    Returns:
        List of App instances.
    """
    apps = []
    files = os.listdir(macro_folder)
    files.sort()

    for filename in files:
        if filename.endswith(".py") and not filename.startswith("._"):
            try:
                module = __import__(macro_folder + "/" + filename[:-3])
                apps.append(App(module.app))
            except (SyntaxError, ImportError, AttributeError, KeyError,
                    NameError, IndexError, TypeError) as err:
                print(f"ERROR in {filename}")
                import traceback
                traceback.print_exception(err, err, err.__traceback__)

    return apps


def setup_display(macropad):
    """Create and configure the display layout.

    Args:
        macropad: MacroPad instance.

    Returns:
        DisplayIO group with all labels configured.
    """
    group = displayio.Group()

    # Create labels for 12 keys (3x4 grid)
    for key_index in range(12):
        x = key_index % 3
        y = key_index // 3
        group.append(
            label.Label(
                terminalio.FONT,
                text="",
                color=0xFFFFFF,
                anchored_position=(
                    (macropad.display.width - 1) * x / 2,
                    macropad.display.height - 1 - (3 - y) * 12,
                ),
                anchor_point=(x / 2, 1.0),
            )
        )

    # App name background
    group.append(Rect(0, 0, macropad.display.width, 12, fill=0xFFFFFF))

    # App name label
    group.append(
        label.Label(
            terminalio.FONT,
            text="",
            color=0x000000,
            anchored_position=(macropad.display.width // 2, -2),
            anchor_point=(0.5, -0.2),
        )
    )

    return group


def animate_label(label_obj, last_move_time, macropad, speed=5):
    """Animate label scrolling across screen.

    Args:
        label_obj: Label object to animate.
        last_move_time: Timestamp of last movement.
        macropad: MacroPad instance.
        speed: Pixels to move per second. Default is 5.

    Returns:
        Updated last_move_time.
    """
    current_time = time.time()
    if current_time - last_move_time >= 1:
        label_obj.x += speed
        if label_obj.x > macropad.display.width:
            label_obj.x = -label_obj.bounding_box[2]
        macropad.display.refresh()
        return current_time
    return last_move_time


def handle_neokey_buttons(debouncers, neokey_manager, macropad):
    """Process NeoKey button presses.

    Args:
        debouncers: List of Debouncer instances.
        neokey_manager: NeoKeyManager instance.
        macropad: MacroPad instance.
    """
    keys = neokey_manager.get_keys()

    # Key mappings: ESC, Vol+, Vol-, Play/Pause
    key_mapping = [
        Keycode.ESCAPE,
        ConsumerControlCode.VOLUME_INCREMENT,
        ConsumerControlCode.VOLUME_DECREMENT,
        ConsumerControlCode.PLAY_PAUSE
    ]

    color_pressed = 0x800080  # Purple

    for i in range(4):
        debouncers[i].update(keys[i])

        if debouncers[i].is_pressed():
            neokey_manager.set_pixel(i, color_pressed)

            if i == 0:  # Keycode (ESC)
                macropad.keyboard.press(key_mapping[i])
                macropad.keyboard.release_all()
            else:  # Consumer control codes
                macropad.consumer_control.release()
                macropad.consumer_control.press(key_mapping[i])
        else:
            neokey_manager.set_pixel(i, color_pressed)

    macropad.consumer_control.release()


def execute_macro_sequence(sequence, pressed, key_number, macropad,
                           display_manager, apps, app_index):
    """Execute a macro key sequence.

    Args:
        sequence: List of macro actions (keycodes, delays, strings, dicts).
        pressed: True if key pressed, False if released.
        key_number: Index of the key (0-12).
        macropad: MacroPad instance.
        display_manager: DisplayManager instance.
        apps: List of all App instances.
        app_index: Current app index.

    Returns:
        Updated activity timestamp.
    """
    start_time = time.time()

    if pressed:
        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.press(item)
                else:
                    macropad.keyboard.release(-item)
            elif isinstance(item, float):
                time.sleep(item)
            elif isinstance(item, str):
                macropad.keyboard_layout.write(item)
            elif isinstance(item, list):
                for code in item:
                    if isinstance(code, int):
                        macropad.consumer_control.release()
                        macropad.consumer_control.press(code)
                    elif isinstance(code, float):
                        time.sleep(code)
            elif isinstance(item, dict):
                handle_special_macro(item, macropad, display_manager)
    else:
        # Release pressed keys/buttons
        for item in sequence:
            if isinstance(item, int) and item >= 0:
                macropad.keyboard.release(item)
            elif isinstance(item, dict):
                if "buttons" in item and item["buttons"] >= 0:
                    macropad.mouse.release(item["buttons"])
                elif "tone" in item:
                    macropad.stop_tone()

        macropad.consumer_control.release()

        if key_number < 12:
            macropad.pixels[key_number] = apps[app_index].macros[key_number][0]
            macropad.pixels.show()

    return start_time


def handle_special_macro(item, macropad, display_manager):
    """Handle special macro commands (brightness, etc).

    Args:
        item: Dictionary with special commands.
        macropad: MacroPad instance.
        display_manager: DisplayManager instance.
    """
    if "test_string" not in item:
        return

    command = item["test_string"]

    if "increase_brightness" in command:
        display_manager.adjust_brightness(0.1, macropad)
    elif "decrease_brightness" in command:
        display_manager.adjust_brightness(-0.1, macropad)


# INITIALIZATION -----------------------

print("Initializing MacroPad...")
macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False
macropad.display.brightness = 0.0
macropad.pixels.brightness = INITIAL_BRIGHTNESS

# Initialize NeoKey with resilience
print("Initializing NeoKey...")
i2c_bus = board.I2C()
neokey_manager = NeoKeyManager(i2c_bus, brightness=INITIAL_BRIGHTNESS * 0.1)

# Set up display
group = setup_display(macropad)
macropad.display.root_group = group

# Load macro applications
print("Loading macro applications...")
apps = load_apps(MACRO_FOLDER)

if not apps:
    group[13].text = "NO MACRO FILES"
    macropad.display.refresh()
    while True:
        pass

# Initialize state
display_manager = DisplayManager(INITIAL_BRIGHTNESS)
neokey_debouncers = [Debouncer() for _ in range(4)]

last_position = None
last_encoder_switch = macropad.encoder_switch_debounced.pressed
app_index = 0
apps[app_index].switch(macropad, group)

activity_time = time.time()
last_animation_time = activity_time

print("Starting main loop...")

# MAIN LOOP ----------------------------

while True:
    # Handle NeoKey buttons
    handle_neokey_buttons(neokey_debouncers, neokey_manager, macropad)

    # Animate app name
    last_animation_time = animate_label(
        group[13], last_animation_time, macropad
    )

    # Manage sleep
    display_manager.manage_sleep(
        activity_time, SLEEP_TIME, macropad, neokey_manager
    )

    # Update NeoKey connection status in app name
    if not neokey_manager.is_connected:
        if "[!]" not in group[13].text:
            group[13].text = f"{apps[app_index].name} [!]"
    else:
        if "[!]" in group[13].text:
            group[13].text = apps[app_index].name

    # Handle encoder rotation
    position = macropad.encoder
    if position != last_position:
        app_index = position % len(apps)
        apps[app_index].switch(macropad, group)
        last_position = position
        activity_time = display_manager.wake_display(macropad, neokey_manager)

    # Handle encoder button
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed

    if encoder_switch != last_encoder_switch:
        activity_time = display_manager.wake_display(macropad, neokey_manager)
        last_encoder_switch = encoder_switch

        if len(apps[app_index].macros) < 13:
            continue

        key_number = 12
        pressed = encoder_switch
    else:
        event = macropad.keys.events.get()
        if not event or event.key_number >= len(apps[app_index].macros):
            continue

        key_number = event.key_number
        pressed = event.pressed

    # Execute macro sequence
    sequence = apps[app_index].macros[key_number][2]
    activity_time = execute_macro_sequence(
        sequence, pressed, key_number, macropad,
        display_manager, apps, app_index
    )