# NeoKey 4-Key Macro Pad Setup

This guide explains how to use the **Adafruit LED Glasses Driver nRF52840** with the **NeoKey 1x4 QT** as a 4-key macro pad.

## Hardware Required

- **Adafruit LED Glasses Driver - nRF52840 Sensor Board** ([Product page](https://www.adafruit.com/product/5217))
- **Adafruit NeoKey 1x4 QT I2C** ([Product page](https://www.adafruit.com/product/4980))
- **STEMMA QT / Qwiic cable** (included with NeoKey)
- USB-C cable for programming and use

## Hardware Connection

1. Connect the NeoKey 1x4 to the LED Glasses Driver using the STEMMA QT cable
2. Plug the left STEMMA QT port on the LED Glasses Driver to either port on the NeoKey
3. Connect USB-C to your computer

```
┌─────────────────────┐      STEMMA QT       ┌─────────────────────┐
│  LED Glasses Driver │ ◄──────────────────► │    NeoKey 1x4 QT    │
│      nRF52840       │                      │   [1] [2] [3] [4]   │
│                     │                      │    ○   ○   ○   ○    │
└─────────────────────┘                      └─────────────────────┘
        │
        │ USB-C
        ▼
    Computer
```

## Software Setup

### 1. Install CircuitPython 10

Download CircuitPython 10.x for the LED Glasses Driver from:
https://circuitpython.org/board/adafruit_led_glasses_nrf52840/

Follow Adafruit's guide to flash CircuitPython to the board.

### 2. Copy Required Libraries

Copy these folders/files from `lib_10x/` to the `lib/` folder on your CIRCUITPY drive:

```
CIRCUITPY/lib/
├── adafruit_hid/          (entire folder)
│   ├── __init__.mpy
│   ├── consumer_control.mpy
│   ├── consumer_control_code.mpy
│   ├── keyboard.mpy
│   ├── keyboard_layout_us.mpy
│   └── keycode.mpy
└── adafruit_seesaw/       (entire folder)
    ├── __init__.mpy
    ├── neopixel.mpy
    └── seesaw.mpy
```

### 3. Copy Code and Macros

```bash
# Copy the main code file (rename to code.py)
cp code_neokey.py /Volumes/CIRCUITPY/code.py

# Copy the macros folder
cp -r macros_4key /Volumes/CIRCUITPY/
```

Or manually:
1. Copy `code_neokey.py` to your CIRCUITPY drive and rename it to `code.py`
2. Copy the entire `macros_4key/` folder to your CIRCUITPY drive

### 4. Final File Structure

Your CIRCUITPY drive should look like:

```
CIRCUITPY/
├── code.py                  (renamed from code_neokey.py)
├── lib/
│   ├── adafruit_hid/
│   └── adafruit_seesaw/
└── macros_4key/
    ├── a_media.py           (first macro file loaded)
    ├── b_productivity.py
    └── c_zoom.py
```

## Customizing Macros

The system loads the **first .py file** (alphabetically) from the `macros_4key/` folder.

### Macro File Format

```python
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode

app = {
    "name": "My Macros",
    "macros": [
        # Format: (COLOR, LABEL, SEQUENCE)
        (0x00FF00, "Key1", [Keycode.A]),              # Key 0
        (0x0000FF, "Key2", [Keycode.B]),              # Key 1
        (0xFF0000, "Key3", [Keycode.C]),              # Key 2
        (0xFFFF00, "Key4", [Keycode.D]),              # Key 3
    ],
}
```

### Color Values

Colors are RGB hex values:
- `0xFF0000` = Red
- `0x00FF00` = Green
- `0x0000FF` = Blue
- `0xFFFF00` = Yellow
- `0xFF00FF` = Magenta
- `0x00FFFF` = Cyan
- `0xFFFFFF` = White
- `0x800080` = Purple

### Macro Sequence Types

| Type | Example | Description |
|------|---------|-------------|
| **Keycode** | `Keycode.A` | Press a keyboard key |
| **Negative Keycode** | `-Keycode.A` | Release a specific key |
| **Multiple Keys** | `[Keycode.CTRL, Keycode.C]` | Press multiple keys (combo) |
| **Consumer Control** | `[[ConsumerControlCode.VOLUME_UP]]` | Media keys (note: double brackets) |
| **String** | `"Hello"` | Type a string |
| **Delay** | `0.1` | Wait 0.1 seconds |

### Example Macros

**Simple key:**
```python
(0xFF0000, "Enter", [Keycode.ENTER])
```

**Key combination (Ctrl+C):**
```python
(0x00FF00, "Copy", [Keycode.CONTROL, Keycode.C])
```

**Media control:**
```python
(0x0000FF, "Vol+", [[ConsumerControlCode.VOLUME_INCREMENT]])
```

**Type text:**
```python
(0xFFFF00, "Email", ["user@example.com"])
```

**Complex sequence with delays:**
```python
(0xFF00FF, "Login", [
    "username",
    Keycode.TAB,
    0.1,                    # Wait 100ms
    "password123",
    Keycode.ENTER,
])
```

## Switching Macro Sets

To use a different macro set:

1. Rename the files to change alphabetical order, OR
2. Delete/move the macro files you don't want

The first `.py` file (alphabetically) in `macros_4key/` is loaded.

## Troubleshooting

### NeoKey Not Responding

1. Check STEMMA QT cable connection
2. Verify both ends are fully plugged in
3. Check serial console for error messages:
   ```bash
   # On Mac/Linux
   screen /dev/tty.usbmodem* 115200
   ```

### Keys Not Working as Expected

1. Connect to serial console to see debug output
2. Each key press prints which key was pressed
3. Verify your macro file has correct syntax

### LED Colors Wrong

- Check that colors are in `0xRRGGBB` format
- NeoKey uses GRB ordering (handled automatically)

### USB HID Not Working

- Make sure CircuitPython 10.x is installed
- Check that `boot.py` isn't disabling USB HID
- Try a different USB port/cable

## Key Layout

Looking at the NeoKey from above (keys facing you):

```
┌─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │
└─────┴─────┴─────┴─────┘
```

Key 0 is on the left, Key 3 is on the right.
