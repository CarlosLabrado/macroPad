# CircuitPython 10.x Upgrade Guide for MacroPad

This guide documents the changes required to upgrade the MacroPad project from CircuitPython 8.x to 10.x.

## Code Changes Made

### ✅ Fixed: `traceback.print_exception()` Syntax

**Breaking Change:** CircuitPython 10.x uses CPython 3.10+ compatible exception handling.

**Changed in:** `code.py` lines 122 and 617

**Old Syntax (8.x):**
```python
traceback.print_exception(exception, exception, exception.__traceback__, file=f)
```

**New Syntax (10.x):**
```python
traceback.print_exception(exception, file=f)
```

This change was made in two locations:
- Line 122: Inside `CrashLogger.log_crash()`
- Line 617: Inside `load_apps()` error handling

## Required Library Updates

### Install CircuitPython 10.x Bundle

Download and install the **CircuitPython 10.x library bundle** from:
https://circuitpython.org/libraries

The .mpy format did NOT change between CircuitPython 9.x and 10.x, so 9.x libraries are technically compatible. However, it's recommended to use the 10.x bundle to ensure future compatibility.

### Required Libraries for MacroPad

The project needs these libraries in the `/lib` folder on CIRCUITPY:

**Core MacroPad Library:**
- `adafruit_macropad/` (folder with library)

**Display Libraries:**
- `adafruit_display_text/` (folder)
- `adafruit_display_shapes/` (folder)

**Input/HID Libraries:**
- `adafruit_hid/` (folder)
- `adafruit_debouncer.mpy`

**NeoPixel/LED Libraries:**
- `neopixel.mpy`

**I2C Device Libraries (for NeoKey1x4):**
- `adafruit_seesaw/` (folder)
- `adafruit_pixelbuf.mpy`

**Utility Libraries:**
- `adafruit_midi/` (folder)
- `adafruit_ticks.mpy`

### Automated Installation with `circup`

The easiest way to install libraries is using the `circup` tool:

```bash
# Install circup (one-time)
pip install circup

# Update all libraries to CircuitPython 10.x compatible versions
circup install --auto
```

## Testing Checklist

After upgrading to CircuitPython 10.x, test the following:

### ✓ Core Functionality
- [ ] MacroPad boots successfully
- [ ] OLED display shows app names
- [ ] All 12 MacroPad keys work correctly
- [ ] Encoder rotation switches between apps
- [ ] Encoder button press works

### ✓ NeoKey1x4 Extension
- [ ] NeoKey connects successfully on boot (check serial console)
- [ ] All 4 NeoKey buttons work (ESC, Vol+, Vol-, Play/Pause)
- [ ] NeoKey LEDs light up correctly
- [ ] Disconnect indicator `[!]` appears when unplugged
- [ ] Auto-reconnection works after repluggging cable

### ✓ Display Features
- [ ] App name scrolling animation works
- [ ] Sleep mode activates after 1 hour
- [ ] Wake from sleep works (press any key or rotate encoder)
- [ ] Display brightness controls work

### ✓ LED Brightness Controls
- [ ] LED brightness increase/decrease works
- [ ] Screen brightness increase/decrease works
- [ ] Normal mode preset works
- [ ] Night mode preset works
- [ ] Off mode preset works (display completely turns off)

### ✓ Macro Functionality
- [ ] Simple keypresses work (e.g., Ctrl+C)
- [ ] Media controls work (Play/Pause, Volume)
- [ ] Text typing macros work
- [ ] Complex sequences with delays work
- [ ] Special commands (brightness, modes) work

### ✓ Error Handling
- [ ] Crash logging to `/crash_log.txt` works
- [ ] Exceptions are logged with proper tracebacks
- [ ] System continues running after recoverable errors
- [ ] NeoKey disconnection is handled gracefully

### ✓ Memory and Performance
- [ ] No memory errors during operation
- [ ] All macro files load successfully
- [ ] No unexpected slowdowns or freezes
- [ ] Crash log rotation works (when exceeding 10KB)

## Known CircuitPython 10.x Breaking Changes (Not Affecting This Code)

These changes exist in 10.x but don't require code modifications for this project:

- ✅ `displayio.Display` → `busdisplay.BusDisplay` (not used directly)
- ✅ `watchdog.WatchDogTimer.deinit()` removed (not used)
- ✅ `_asyncio` API changes (not used)
- ✅ `synthio` audio changes (not used)
- ✅ `os.uname()` standardization (not relied upon)

## Troubleshooting

### Issue: `ImportError: no module named 'traceback'`
**Solution:** CircuitPython 10.x includes `traceback` as a built-in module. This shouldn't happen, but if it does, ensure the CircuitPython firmware is properly installed.

### Issue: "incompatible mpy file" errors
**Solution:** Delete ALL files in `/lib` and reinstall with the CircuitPython 10.x bundle. Mixed library versions cause this error.

### Issue: NeoKey not connecting
**Solution:**
1. Check STEMMA QT cable connection
2. Verify NeoKey I2C address is 0x30 (default)
3. Check serial console for connection messages
4. Try `i2c_bus.scan()` to verify device is detected

### Issue: Display or macro behavior changed
**Solution:**
1. Verify all libraries are from the 10.x bundle
2. Check serial console for deprecation warnings
3. Review `/crash_log.txt` for detailed error information

### Issue: Memory errors after upgrade
**Solution:**
1. CircuitPython 10.x may have different memory usage
2. Remove unused macro files
3. Simplify complex macro sequences
4. Use `gc.collect()` if implementing additional features

## Additional Resources

- **CircuitPython 10.x Documentation:** https://docs.circuitpython.org/
- **MacroPad Library Docs:** https://docs.circuitpython.org/projects/macropad/en/latest/
- **CircuitPython Library Bundle:** https://circuitpython.org/libraries
- **Adafruit Forums:** https://forums.adafruit.com/
- **CircuitPython GitHub:** https://github.com/adafruit/circuitpython/releases

## Upgrade Steps Summary

1. ✅ Update `code.py` with the fixed `traceback.print_exception()` calls (already done)
2. Download CircuitPython 10.x firmware from https://circuitpython.org/board/adafruit_macropad_rp2040/
3. Install CircuitPython 10.x on the MacroPad (double-tap reset, copy .uf2 file)
4. Download CircuitPython 10.x library bundle
5. Delete old `/lib` folder contents
6. Install required libraries (see list above or use `circup`)
7. Copy updated `code.py` to CIRCUITPY drive
8. Copy `/macros` folder (no changes needed)
9. Test using the checklist above

## Notes

- The upgrade should be smooth with minimal issues
- The main breaking change was the `traceback.print_exception()` syntax
- All other code is compatible with CircuitPython 10.x
- NeoKey1x4 resilience features should work identically
- Display and HID libraries are backward compatible

**Estimated Upgrade Time:** 15-30 minutes

**Risk Level:** Low - only one breaking change affects the code
