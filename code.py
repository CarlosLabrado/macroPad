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

import os
import time
import displayio
import terminalio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from adafruit_macropad import MacroPad

# CONFIGURABLES ------------------------

MACRO_FOLDER = "/macros"
KEY_BRIGHTNESS = 0.1


# CLASSES AND FUNCTIONS ----------------


def wake_display():
    """
    Wakes up the display and sets the brightness of the keys.
    Returns the current time.
    """
    macropad.display_sleep = False
    macropad.pixels.brightness = KEY_BRIGHTNESS
    macropad.pixels.show()
    macropad.display.refresh()
    return time.time()


def sleep_display():
    """
    Puts the display to sleep and turns off the brightness of the keys.
    """
    macropad.display_sleep = True
    macropad.pixels.brightness = 0.0
    macropad.pixels.show()
    macropad.display.refresh()


def increase_brightness(current_brightness, param_max_brightness=1.0, delta=0.1):
    """
    Increase the brightness.

    :param current_brightness: The current brightness level.
    :param param_max_brightness: The maximum brightness that can be achieved. Default is 1.0.
    :param delta: The amount to increase the brightness by. Default is 0.1.
    :return: The new brightness level.
    """
    new_brightness = current_brightness + delta
    new_brightness = min(new_brightness, param_max_brightness)  # Ensure brightness does not exceed max_brightness

    return new_brightness


def decrease_brightness(current_brightness, delta=0.1):
    """
    Decrease the brightness.

    :param current_brightness: The current brightness level.
    :param delta: The amount to decrease the brightness by. Default is 0.1.
    :return: The new brightness level.
    """
    new_brightness = current_brightness - delta
    new_brightness = max(new_brightness, 0.0)  # Ensure brightness does not go below 0.0

    return new_brightness


def pulsate(current_brightness, param_max_brightness, param_pulsating_up, base_delta=0.02):
    """
    # TODO: still needs work, its not working as expected, too fast when pulsating at low brightness
    Create a pulsating effect by increasing and decreasing the brightness.

    :param current_brightness: The current brightness level.
    :param param_max_brightness: The maximum brightness that can be achieved.
    :param param_pulsating_up: A boolean indicating whether the brightness is currently increasing.
    :param base_delta: The base amount to increase or decrease the brightness by. Default is 0.02.
    :return: The new brightness level and the updated direction of pulsation.
    """
    # Calculate delta based on the max brightness
    delta = base_delta * (param_max_brightness / param_max_brightness)

    # Ensure delta does not become too small
    delta = max(delta, 0.001)  # Change this value to adjust the minimum delta

    if param_pulsating_up:
        new_brightness = increase_brightness(current_brightness, param_max_brightness, delta)
        if new_brightness >= param_max_brightness:
            param_pulsating_up = False
    else:
        new_brightness = decrease_brightness(current_brightness, delta)
        # If new_brightness is very close to 0, set it to exactly 0
        if new_brightness < 0.001:  # Change this value to adjust the threshold
            new_brightness = 0.0
        if new_brightness <= 0.0:
            param_pulsating_up = True

    return new_brightness, param_pulsating_up


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

        wake_display()


# INITIALIZATION -----------------------

macropad = MacroPad()
macropad.display.auto_refresh = False
macropad.pixels.auto_write = False
macropad.display.brightness = 0.0  # As dim as possible
macropad.pixels.brightness = KEY_BRIGHTNESS

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

start_time = time.time()
sleep_time = 60 * 60  # minutes

last_move_time = time.time()

# Get the label
label_to_animate = group[13]

# In the main loop
pulsating = False
pulsating_up = True
max_brightness = KEY_BRIGHTNESS
counter = 0  # Counter for skipping cycles

while True:
    # Add this block inside the main loop to create the pulsating effect
    if pulsating:
        counter += 1
        if counter >= 50:  # Change this value to control the speed of the pulsating effect
            KEY_BRIGHTNESS, pulsating_up = pulsate(KEY_BRIGHTNESS, max_brightness, pulsating_up, base_delta=0.02)
            macropad.pixels.brightness = KEY_BRIGHTNESS
            macropad.pixels.show()
            counter = 0  # Reset the counter

    # Animate the label
    current_time = time.time()
    if current_time - last_move_time >= 1:  # 1 second has passed
        label_to_animate.x += 5  # Change this value to control the speed of the animation
        if label_to_animate.x > macropad.display.width:
            label_to_animate.x = -label_to_animate.bounding_box[2]  # Reset position
        last_move_time = current_time  # Update the move time

        # Refresh the display after updating the label's position
        macropad.display.refresh()

    # sleep display logic
    current_time = time.time()
    elapsed_time = current_time - start_time
    # Check if 60 minutes have passed
    if elapsed_time >= sleep_time:
        sleep_display()

    # Read encoder position. If it's changed, switch apps.
    position = macropad.encoder
    if position != last_position:
        app_index = position % len(apps)
        apps[app_index].switch()
        last_position = position

        start_time = wake_display()

    # Handle encoder button. If state has changed, and if there's a
    # corresponding macro, set up variables to act on this just like
    # the keypad keys, as if it were a 13th key/macro.
    macropad.encoder_switch_debounced.update()
    encoder_switch = macropad.encoder_switch_debounced.pressed
    if encoder_switch != last_encoder_switch:
        start_time = wake_display()

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
    if pressed:
        start_time = wake_display()

        # 'sequence' is an arbitrary-length list, each item is one of:
        # Positive integer (e.g. Keycode.KEYPAD_MINUS): key pressed
        # Negative integer: (absolute value) key released
        # Float (e.g. 0.25): delay in seconds
        # String (e.g. "Foo"): corresponding keys pressed & released
        # List []: one or more Consumer Control codes (can also do float delay)
        # Dict {}: mouse buttons/motion (might extend in future)
        if key_number < 12:  # No pixel for encoder button
            macropad.pixels[key_number] = 0xFFFFFF
            macropad.pixels.show()
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
                    if isinstance(code, float):
                        time.sleep(code)
            elif isinstance(item, dict):
                if "test_string" in item:
                    internal_selection = item["test_string"]
                    if "toggle_effect" in internal_selection:
                        pulsating = not pulsating
                    elif "increase_brightness" in internal_selection:
                        KEY_BRIGHTNESS = increase_brightness(KEY_BRIGHTNESS, param_max_brightness=1.0, delta=0.1)
                        max_brightness = KEY_BRIGHTNESS
                        macropad.pixels.brightness = KEY_BRIGHTNESS
                        macropad.pixels.show()
                    elif "decrease_brightness" in internal_selection:
                        KEY_BRIGHTNESS = decrease_brightness(KEY_BRIGHTNESS, delta=0.1)
                        max_brightness = KEY_BRIGHTNESS
                        macropad.pixels.brightness = KEY_BRIGHTNESS
                        macropad.pixels.show()
                if "buttons" in item:
                    if item["buttons"] >= 0:
                        macropad.mouse.press(item["buttons"])
                    else:
                        macropad.mouse.release(-item["buttons"])
                macropad.mouse.move(
                    item["x"] if "x" in item else 0,
                    item["y"] if "y" in item else 0,
                    item["wheel"] if "wheel" in item else 0,
                )
                if "tone" in item:
                    if item["tone"] > 0:
                        macropad.stop_tone()
                        macropad.start_tone(item["tone"])
                    else:
                        macropad.stop_tone()
                elif "play" in item:
                    macropad.play_file(item["play"])

    else:
        # Release any still-pressed keys, consumer codes, mouse buttons
        # Keys and mouse buttons are individually released this way (rather
        # than release_all()) because pad supports multi-key rollover, e.g.
        # could have a meta key or right-mouse held down by one macro and
        # press/release keys/buttons with others. Navigate popups, etc.
        for item in sequence:
            if isinstance(item, int):
                if item >= 0:
                    macropad.keyboard.release(item)
            elif isinstance(item, dict):
                if "buttons" in item:
                    if item["buttons"] >= 0:
                        macropad.mouse.release(item["buttons"])
                elif "tone" in item:
                    macropad.stop_tone()
        macropad.consumer_control.release()
        if key_number < 12:  # No pixel for encoder button
            macropad.pixels[key_number] = apps[app_index].macros[key_number][0]
            macropad.pixels.show()
