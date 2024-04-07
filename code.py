# SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
A macro/hotkey program for Adafruit MACROPAD. Macro setups are stored in the
/macros folder (configurable below), load up just the ones you're likely to
use. Plug into computer's USB port, use dial to select an application macro
set, press MACROPAD keys to send key sequences and other USB protocols.
"""

# pylint: disable=import-error, unused-import, too-few-public-methods

## IMPORTANT we are using circuitpython 8x

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

# CONFIGURABLES ------------------------

MACRO_FOLDER = "/macros"
global_key_brightness = 0.1

from micropython import const
from adafruit_seesaw import neopixel
from adafruit_seesaw.seesaw import Seesaw

try:
    import typing  # pylint: disable=unused-import
    from busio import I2C
except ImportError:
    pass

_NEOKEY1X4_ADDR = const(0x30)

_NEOKEY1X4_NEOPIX_PIN = const(3)

_NEOKEY1X4_NUM_ROWS = const(1)
_NEOKEY1X4_NUM_COLS = const(4)
_NEOKEY1X4_NUM_KEYS = const(4)


class NeoKey1x4(Seesaw):
    """Driver for the Adafruit NeoKey 1x4."""

    def __init__(
            self, i2c_bus: I2C, interrupt: bool = False, addr: int = _NEOKEY1X4_ADDR, brightness: float = 0.01
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
        # set the pins to inputs, pullups
        for b in range(4, 8):
            self.pin_mode(b, self.INPUT_PULLUP)

    def __getitem__(self, index: int) -> bool:
        if not isinstance(index, int) or (index < 0) or (index > 3):
            raise RuntimeError("Index must be 0 thru 3")
        return not self.digital_read(index + 4)

    def get_keys(self) -> typing.List[bool]:
        """Read all 4 keys at once and return an array of booleans.

        Returns:
            typing.List[bool]: _description_
        """
        # use a bit mask with ports 4-7 to read all 4 keys at once
        bulk_read = self.digital_read_bulk(0xF0)

        # convert the leftmost 4 bits to an array of booleans and return
        keys = [bulk_read & (1 << i) == 0 for i in range(4, 8)]
        return keys


# Initialize the NeoKey object
i2c_bus = board.I2C()
neokey = NeoKey1x4(i2c_bus, addr=0x30, brightness=global_key_brightness * 0.1)


class App:
    """Class representing a host-side application, for which we have a set
    of macro sequences. Project code was originally more complex and
    this was helpful, but maybe it's excessive now?"""

    def __init__(self, appdata):
        """
        Initialize the App instance.

        :param appdata: A dictionary containing the application data.
        """
        self.name = appdata["name"]
        self.macros = appdata["macros"]

    def switch(self):
        """
        Activate application settings; update OLED labels and LED
        colors.
        """
        group[13].text = self.name  # Application name
        for i in range(12):
            if i < len(self.macros):  # Key in use, set label + LED color
                macropad.pixels[i] = self.macros[i][0]
                group[i].text = self.macros[i][1]
            else:  # Key not in use, no label or LED
                macropad.pixels[i] = 0
                group[i].text = ""
        macropad.keyboard.release_all()
        macropad.consumer_control.release()
        macropad.mouse.release_all()
        macropad.stop_tone()
        macropad.pixels.show()
        macropad.display.refresh()


# INITIALIZATION -----------------------

macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False
macropad.display.brightness = 0.0  # As dim as possible
macropad.pixels.brightness = global_key_brightness

# Set up displayio group with all the labels
group = displayio.Group()
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
group.append(Rect(0, 0, macropad.display.width, 12, fill=0xFFFFFF))
group.append(
    label.Label(
        terminalio.FONT,
        text="",
        color=0x000000,
        anchored_position=(macropad.display.width // 2, -2),
        anchor_point=(0.5, -0.2),
    )
)
macropad.display.root_group = group

# Load all the macro key setups from .py files in MACRO_FOLDER
apps = []
files = os.listdir(MACRO_FOLDER)
files.sort()
for filename in files:
    if filename.endswith(".py") and not filename.startswith("._"):
        try:
            module = __import__(MACRO_FOLDER + "/" + filename[:-3])
            apps.append(App(module.app))
        except (
                SyntaxError,
                ImportError,
                AttributeError,
                KeyError,
                NameError,
                IndexError,
                TypeError,
        ) as err:
            print("ERROR in", filename)
            import traceback

            traceback.print_exception(err, err, err.__traceback__)

if not apps:
    group[13].text = "NO MACRO FILES FOUND"
    macropad.display.refresh()
    while True:
        pass

last_position = None
last_encoder_switch = macropad.encoder_switch_debounced.pressed
app_index = 0
apps[app_index].switch()

# MAIN LOOP ----------------------------

global_start_time = time.time()
# sleep_time = 60 * 60  # minutes
sleep_time = 10  # secs

last_move_time = global_start_time

# Get the label
label_to_animate = group[13]


class Debouncer:
    def __init__(self):
        self.state = False
        self.last_state = False

    def update(self, new_state):
        self.last_state = self.state
        self.state = new_state

    def is_pressed(self):
        return self.state and not self.last_state


# Create debouncers for each key
debouncers = [Debouncer() for _ in range(4)]

# Define a list of colors for each key
colors = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF]


def update_debouncers(debouncers_param, neokey_param):
    for i in range(4):  # Only for the new keys
        debouncers_param[i].update(neokey_param[i])


def check_buttons(debouncers_param, neokey_param, colors_param, macropad_param):
    key_mapping = [Keycode.ESCAPE, ConsumerControlCode.VOLUME_INCREMENT, ConsumerControlCode.VOLUME_DECREMENT,
                   ConsumerControlCode.PLAY_PAUSE]
    for i in range(4):  # Only for the new keys
        # There's a different logic for pressing Keycodes and Consumer control codes
        if debouncers_param[i].is_pressed():
            neokey_param.pixels[i] = colors_param[i]  # Use the color corresponding to the button
            if i == 0:
                macropad_param.keyboard.press(key_mapping[i])  # Press the corresponding key
                macropad_param.keyboard.release_all()  # Release all keys
            else:
                macropad_param.consumer_control.release()
                macropad_param.consumer_control.press(key_mapping[i])
        else:
            neokey_param.pixels[i] = 0xFF0000
    macropad_param.consumer_control.release()


def animate_label(label_to_animate_param, last_move_time_param, macropad_param):
    inner_current_time = time.time()
    if inner_current_time - last_move_time_param >= 1:  # 1 second has passed
        label_to_animate_param.x += 5  # Change this value to control the speed of the animation
        if label_to_animate_param.x > macropad_param.display.width:
            label_to_animate_param.x = -label_to_animate_param.bounding_box[2]  # Reset position
        last_move_time_param = inner_current_time  # Update the move time
        macropad_param.display.refresh()
    return last_move_time_param


def execute_sequence(pressed_param, sequence_param, macropad_param, max_brightness, start_time, display_manager_param):
    if pressed_param:
        start_time = display_manager_param.wake_display(macropad_param=macropad_param)

        for item in sequence_param:
            if isinstance(item, int):
                if item >= 0:
                    macropad_param.keyboard.press(item)
                else:
                    macropad_param.keyboard.release(-item)
            elif isinstance(item, float):
                time.sleep(item)
            elif isinstance(item, str):
                macropad_param.keyboard_layout.write(item)
            elif isinstance(item, list):
                for code in item:
                    if isinstance(code, int):
                        macropad_param.consumer_control.release()
                        macropad_param.consumer_control.press(code)
                    if isinstance(code, float):
                        time.sleep(code)
            elif isinstance(item, dict):
                handle_dict_item(item_param=item, macropad_param=macropad_param,
                                 max_brightness=max_brightness, display_manager_param=display_manager_param)
    else:
        # Release any still-pressed keys, consumer codes, mouse buttons
        # Keys and mouse buttons are individually released this way (rather
        # than release_all()) because pad supports multi-key rollover, e.g.
        # could have a meta key or right-mouse held down by one macro and
        # press/release keys/buttons with others. Navigate popups, etc.
        for item in sequence_param:
            if isinstance(item, int):
                if item >= 0:
                    macropad_param.keyboard.release(item)
            elif isinstance(item, dict):
                if "buttons" in item:
                    if item["buttons"] >= 0:
                        macropad_param.mouse.release(item["buttons"])
                elif "tone" in item:
                    macropad_param.stop_tone()
        macropad_param.consumer_control.release()
        if key_number < 12:  # No pixel for encoder button
            macropad_param.pixels[key_number] = apps[app_index].macros[key_number][0]
            macropad_param.pixels.show()
    return start_time


def handle_dict_item(item_param, macropad_param, max_brightness, display_manager_param):
    if "test_string" in item_param:
        internal_selection = item_param["test_string"]
        if "toggle_effect" in internal_selection:
            pass  # TODO: Implement the toggle effect
        elif "increase_brightness" in internal_selection:
            max_brightness = display_manager_param.increase_brightness(max_brightness, param_max_brightness=1.0,
                                                                       delta=0.1)
            max_brightness = max_brightness
            macropad_param.pixels.brightness = max_brightness
            macropad_param.pixels.show()
        elif "decrease_brightness" in internal_selection:
            max_brightness = display_manager_param.decrease_brightness(max_brightness, delta=0.1)
            max_brightness = max_brightness
            macropad_param.pixels.brightness = max_brightness
            macropad_param.pixels.show()


class DisplayManager:
    def __init__(self, initial_brightness):
        self.is_display_asleep = False
        self.global_key_brightness = initial_brightness
        self.last_known_brightness = initial_brightness

    def wake_display(self, macropad_param):
        if self.is_display_asleep:
            print("Waking up display")
            self.restore_brightness()
            macropad_param.display_sleep = False
            macropad_param.pixels.brightness = self.global_key_brightness
            macropad_param.pixels.show()
            macropad_param.display.refresh()
            self.is_display_asleep = False
        return time.time()

    def sleep_display(self, macropad_param):
        if not self.is_display_asleep:
            print("Putting display to sleep")
            self.save_brightness_state()
            self.global_key_brightness = 0.0
            macropad_param.display_sleep = True
            macropad_param.pixels.brightness = self.global_key_brightness
            macropad_param.pixels.show()
            macropad_param.display.refresh()
            self.is_display_asleep = True

    def restore_brightness(self):
        self.global_key_brightness = self.last_known_brightness

    def save_brightness_state(self):
        self.last_known_brightness = self.global_key_brightness

    def manage_sleep_logic(self, start_time, sleep_time_param, macropad_param, neokey_param):
        inner_current_time = time.time()
        elapsed_time = inner_current_time - start_time
        if elapsed_time >= sleep_time_param and not self.is_display_asleep:
            self.sleep_display(macropad_param=macropad_param)
            neokey_param.pixels.brightness = self.global_key_brightness
        return inner_current_time

    def increase_brightness(self, current_brightness, param_max_brightness=1.0, delta=0.1):
        """
        Increase the brightness.
        # TODO fix this, is only increasing once

        :param current_brightness: The current brightness level.
        :param param_max_brightness: The maximum brightness that can be achieved. Default is 1.0.
        :param delta: The amount to increase the brightness by. Default is 0.1.
        :return: The new brightness level.
        """
        print("Increasing brightness")
        new_brightness = current_brightness + delta
        new_brightness = min(new_brightness, param_max_brightness)  # Ensure brightness does not exceed max_brightness

        self.global_key_brightness = new_brightness
        return new_brightness

    def decrease_brightness(self, current_brightness, delta=0.1):
        """
        Decrease the brightness.

        :param current_brightness: The current brightness level.
        :param delta: The amount to decrease the brightness by. Default is 0.1.
        :return: The new brightness level.
        """
        print("Decreasing brightness")
        new_brightness = current_brightness - delta
        new_brightness = max(new_brightness, 0.0)  # Ensure brightness does not go below 0.0

        self.global_key_brightness = new_brightness
        return new_brightness


display_manager = DisplayManager(initial_brightness=0.1)

while True:
    update_debouncers(debouncers_param=debouncers, neokey_param=neokey)
    check_buttons(debouncers_param=debouncers, neokey_param=neokey, colors_param=colors, macropad_param=macropad)
    neokey.pixels.brightness = display_manager.global_key_brightness

    last_move_time = animate_label(label_to_animate_param=label_to_animate, last_move_time_param=last_move_time,
                                   macropad_param=macropad)
    #
    # print(f"sleep_time: {sleep_time}")
    # print(f"global_start_time: {global_start_time}")
    display_manager.manage_sleep_logic(start_time=global_start_time,
                                       sleep_time_param=sleep_time,
                                       macropad_param=macropad, neokey_param=neokey)

    # print(f"global_start_time: {global_start_time}")

    # Read encoder position. If it's changed, switch apps.
    position = macropad.encoder
    if position != last_position:
        app_index = position % len(apps)
        apps[app_index].switch()
        last_position = position

        global_start_time = display_manager.wake_display(macropad_param=macropad)
        # print(f"encoder global_start_time: {global_start_time}")

    # Handle encoder button. If state has changed, and if there's a
    # corresponding macro, set up variables to act on this just like
    # the keypad keys, as if it were a 13th key/macro.
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed
    if encoder_switch != last_encoder_switch:
        global_start_time = display_manager.wake_display(macropad_param=macropad)
        # print(f"encoder switch global_start_time: {global_start_time}")

        last_encoder_switch = encoder_switch
        if len(apps[app_index].macros) < 13:
            continue  # No 13th macro, just resume main loop
        key_number = 12  # else process below as 13th macro
        pressed = encoder_switch
    else:
        event = macropad.keys.events.get()
        if not event or event.key_number >= len(apps[app_index].macros):
            continue  # No key events, or no corresponding macro, resume loop
        key_number = event.key_number
        pressed = event.pressed

    # If code reaches here, a key or the encoder button WAS pressed/released
    # and there IS a corresponding macro available for it...other situations
    # are avoided by 'continue' statements above which resume the loop.

    sequence = apps[app_index].macros[key_number][2]
    global_start_time = execute_sequence(pressed_param=pressed, sequence_param=sequence,
                                         macropad_param=macropad,
                                         max_brightness=global_key_brightness,
                                         start_time=global_start_time,
                                         display_manager_param=display_manager)
    # print(f" popo global_start_time: {global_start_time}")
