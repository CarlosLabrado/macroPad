# Configuration macros for brightness and mode control

app = {
    "name": "Configuration",
    "macros": [
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ---------- LED Controls
        (0xFF4500, "LED+", [{"test_string": "increase_brightness"}]),
        (0xFF4500, "LED-", [{"test_string": "decrease_brightness"}]),
        (0x000000, "", []),
        # 2nd row ---------- Screen Controls
        (0x4169E1, "Screen+", [{"test_string": "increase_screen_brightness"}]),
        (0x4169E1, "Screen-", [{"test_string": "decrease_screen_brightness"}]),
        (0x000000, "", []),
        # 3rd row ---------- Mode Presets
        (0x00FF00, "Normal", [{"test_string": "normal_mode"}]),
        (0x0000FF, "Night", [{"test_string": "night_mode"}]),
        (0x000000, "", []),
        # 4th row ---------- Reserved
        (0xFF0000, "Off", [{"test_string": "off_mode"}]),
        (0x000000, "", []),
        (0x000000, "", []),
        # Encoder button ---
        (0x00FF00, "Normal", [{"test_string": "normal_mode"}]),
    ],
}
