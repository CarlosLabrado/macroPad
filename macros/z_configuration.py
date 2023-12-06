app = {  # REQUIRED dict, must be named 'app'
    "name": "configuration",  # Application name
    "macros": [  # List of button macros...
        # COLOR    LABEL    KEY SEQUENCE
        # 1st row ----------
        (0x200000, "inc", [{"test_string": "increase_brightness"}]),
        (0x200000, "dec", [{"test_string": "decrease_brightness"}]),
        (0x200000, "", []),
        # 2nd row ----------
        (0x200000, "", []),
        (0x200000, "", []),
        (0x200000, "", []),
        # 3rd row ----------
        (0x200000, "", []),
        (0x200000, "", []),
        (0x200000, "", []),
        # 4th row ----------
        (0x200000, "", []),
        (0x200000, "", []),
        (0x200000, "", []),
        # Encoder button ---
        (0x000000, "", []),
    ],
}
