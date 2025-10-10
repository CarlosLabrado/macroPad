# MacroPad with NeoKey1x4 Extension

A production-ready CircuitPython macro keyboard system for Adafruit MacroPad with resilient NeoKey1x4 STEMMA QT extension support.

## Features

- **12 programmable macro keys** on MacroPad + **4 additional keys** on NeoKey1x4
- **Automatic sleep/wake** after 1 hour of inactivity
- **Resilient NeoKey connection** - auto-reconnects if disconnected
- **Brightness control** via macro commands
- **Scrolling app name display**
- **Visual disconnect indicator** shows `[!]` when NeoKey is offline

## Hardware Requirements

- Adafruit MacroPad RP2040
- Adafruit NeoKey 1x4 QT I2C
- STEMMA QT cable (connecting MacroPad to NeoKey)

## Installation

1. Install CircuitPython 8.x on your MacroPad
2. Copy `code.py` to the root of your CIRCUITPY drive
3. Create a `/macros` folder on CIRCUITPY
4. Add your macro files (see below)

## Directory Structure

```
CIRCUITPY/
├── code.py                 # Main program (this file)
├── macros/                 # Macro definitions folder
│   ├── a_basic.py         # Example: media controls
│   ├── b_windows.py       # Example: Windows shortcuts
│   └── c_custom.py        # Your custom macros
└── lib/                   # Required libraries
    ├── adafruit_macropad/
    ├── adafruit_seesaw/
    └── ...
```

## Creating Macro Files

Each macro file in `/macros` defines one "app" - a set of 12 key bindings plus an optional encoder button binding.

### Basic Structure

```python
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keycode import Keycode

app = {
    "name": "My App",
    "macros": [
        # (COLOR, LABEL, SEQUENCE)
        (0xFF0000, "Red", [Keycode.A]),                    # Key 1
        (0x00FF00, "Green", [Keycode.B, 0.1, Keycode.C]),  # Key 2
        (0x0000FF, "Type", ["Hello World"]),               # Key 3
        # ... up to 12 keys
        (0xFFFFFF, "Enc", [Keycode.ENTER]),                # Encoder (optional)
    ]
}
```

### Macro Sequence Format

Each key's sequence is a list that can contain:

- **Keycodes**: `Keycode.A`, `Keycode.CONTROL` (positive = press, negative = release)
- **Delays**: `0.1` (float = pause in seconds)
- **Strings**: `"text to type"` (typed literally)
- **Consumer codes**: `[[ConsumerControlCode.VOLUME_UP]]` (note double brackets!)
- **Special commands**: `{"test_string": "increase_brightness"}` (see below)

### Examples

**Simple keypress:**
```python
(0xFF0000, "Ctrl+C", [Keycode.CONTROL, Keycode.C])
```

**Media control:**
```python
(0x00FF00, "Play", [[ConsumerControlCode.PLAY_PAUSE]])
```

**Type text:**
```python
(0x0000FF, "Email", ["user@example.com"])
```

**Complex sequence with delays:**
```python
(0xFFFF00, "Multi", [
    Keycode.CONTROL, 
    Keycode.C,           # Ctrl+C
    -Keycode.CONTROL,    # Release Ctrl
    0.5,                 # Wait 500ms
    Keycode.TAB,         # Tab
    0.1,
    Keycode.CONTROL,
    Keycode.V,           # Ctrl+V
])
```

**Special commands:**
```python
# LED brightness controls (MacroPad + NeoKey keys)
(0xFF4500, "LED+", [{"test_string": "increase_brightness"}])
(0xFF4500, "LED-", [{"test_string": "decrease_brightness"}])

# Screen brightness controls (OLED display only)
(0x4169E1, "Scrn+", [{"test_string": "increase_screen_brightness"}])
(0x4169E1, "Scrn-", [{"test_string": "decrease_screen_brightness"}])

# Preset modes
(0x00FF00, "Normal", [{"test_string": "normal_mode"}])     # Default brightness
(0x0000FF, "Night", [{"test_string": "night_mode"}])      # Very dim for night use
(0xFF0000, "Off", [{"test_string": "off_mode"}])          # Turn off all displays/LEDs
```

Available special commands:
- `increase_brightness` - Increase LED brightness by 0.1 (MacroPad + NeoKey keys)
- `decrease_brightness` - Decrease LED brightness by 0.1 (MacroPad + NeoKey keys)
- `increase_screen_brightness` - Increase OLED brightness by 0.1 (screen only)
- `decrease_screen_brightness` - Decrease OLED brightness by 0.1 (screen only)
- `normal_mode` - Reset to default brightness (LEDs: 0.1, Screen: 0.0)
- `night_mode` - Very dim mode for night use (LEDs: 0.01, Screen: 0.0)
- `off_mode` - Turn everything off (LEDs: 0.0, Screen: 0.0)
- `toggle_effect` - Reserved for future use

## NeoKey Button Mappings

The 4 NeoKey buttons are hardcoded (change in `handle_neokey_buttons()` if needed):

- **Button 0**: ESC key
- **Button 1**: Volume Up
- **Button 2**: Volume Down
- **Button 3**: Play/Pause

## Brightness Control System

The system has **independent brightness controls**:

### LED Brightness (MacroPad + NeoKey keys)
- Controls the brightness of all 12 MacroPad key LEDs + 4 NeoKey LEDs
- Range: 0.0 (off) to 1.0 (full brightness)
- Controlled via `increase_brightness` / `decrease_brightness` commands

### Screen Brightness (OLED display)
- Controls only the OLED display brightness
- Range: 0.0 (dim) to 1.0 (bright)
- **Note:** Even at 0.0, the OLED is still visible (just very dim)
- Controlled via `increase_screen_brightness` / `decrease_screen_brightness` commands

### Preset Modes
Quick shortcuts to common brightness configurations:

| Mode | LED Brightness | Screen Brightness | Use Case |
|------|----------------|-------------------|----------|
| Normal | 0.1 | 0.0 | Default, everyday use |
| Night | 0.01 | 0.0 | Dark room, minimal light |
| Off | 0.0 | 0.0 | Completely dark |

Access these modes through the "Configuration" app or bind to any key.

## Configuration

Edit these constants at the top of `code.py`:

```python
MACRO_FOLDER = "/macros"                # Macro files location
INITIAL_LED_BRIGHTNESS = 0.1            # Starting LED brightness (0.0-1.0)
INITIAL_SCREEN_BRIGHTNESS = 0.0         # Starting screen brightness (0.0-1.0)
SLEEP_TIME = 60 * 60                    # Sleep after 1 hour (seconds)
NEOKEY_ADDR = 0x30                      # I2C address of NeoKey
NEOKEY_RECONNECT_INTERVAL = 5.0         # Reconnect attempt interval

# Preset brightness modes
NORMAL_LED_BRIGHTNESS = 0.1             # Normal mode LED brightness
NORMAL_SCREEN_BRIGHTNESS = 0.0          # Normal mode screen brightness
NIGHT_LED_BRIGHTNESS = 0.01             # Night mode LED brightness (very dim)
NIGHT_SCREEN_BRIGHTNESS = 0.0           # Night mode screen brightness
OFF_LED_BRIGHTNESS = 0.0                # Off mode LED brightness
OFF_SCREEN_BRIGHTNESS = 0.0             # Off mode screen brightness
```

## Architecture

### Class Structure

```
NeoKey1x4               - Low-level driver for the hardware
NeoKeyManager           - Manages connection/reconnection logic
DisplayManager          - Handles sleep/wake and brightness
Debouncer               - Button debouncing
App                     - Represents one macro application
```

### Key Design Decisions

1. **Single Source of Truth for Brightness**: `DisplayManager` owns all brightness state
2. **Resilient I2C**: NeoKey operations wrapped in try-except with auto-reconnection
3. **Memory Efficient**: Simple reconnection strategy (no complex state machines)
4. **Graceful Degradation**: MacroPad continues working if NeoKey disconnects
5. **Visual Feedback**: Disconnect indicator `[!]` in app name

### Reconnection Strategy

- Failed I2C reads increment a counter
- After 3 consecutive failures, mark as disconnected
- Reconnection attempts every 5 seconds (configurable)
- No blocking - reconnect happens in background
- On wake from sleep, force immediate reconnect attempt

## Troubleshooting

### NeoKey shows [!] indicator

The NeoKey is disconnected. This is normal and handled gracefully:
1. The MacroPad continues working normally
2. NeoKey keys won't respond until reconnected
3. Device will auto-reconnect within 5 seconds after you:
   - Plug the STEMMA QT cable back in
   - Fix the cable connection
   - Power cycle the NeoKey

**Note:** You'll see "NeoKey connection failed" messages in the serial console during reconnection attempts - this is normal and expected when the device is unplugged.

### Memory errors

CircuitPython has limited RAM. Try:
1. Remove unused macro files from `/macros`
2. Simplify macro sequences
3. Reduce number of apps

### Macros not working

1. Check syntax in your `.py` files
2. Look for errors on serial console
3. Ensure macro file is in `/macros` folder
4. File must be named `*.py` (not `._*.py`)

### Display won't wake

Press any key or turn the encoder to wake from sleep.

## Performance Notes

- **Startup time**: ~2-3 seconds to load all macros
- **Sleep timeout**: 1 hour (configurable)
- **Reconnect interval**: 5 seconds (configurable)
- **Animation speed**: Label scrolls at 5 pixels/second

## Memory Usage

Typical usage: ~15-20KB RAM with 3-4 macro apps loaded.

## Contributing

When modifying:
- Use Google docstring format
- Test with NeoKey disconnected and reconnected
- Verify memory usage doesn't exceed limits
- Test all macro types (keycodes, consumer codes, strings)

## License

SPDX-FileCopyrightText: 2021 Phillip Burgess for Adafruit Industries  
SPDX-License-Identifier: MIT

## Version History

- **v2.0** - Refactored architecture with resilient NeoKey support
- **v1.0** - Original implementation