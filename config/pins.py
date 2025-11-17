# Pin Configuration for Raspberry Pi 4 Game Console
# Minimal setup - IR Receiver + Buzzer only

# IR Receiver
IR_PIN = 18  # GPIO 18 (Pin 12)

# Buzzer
BUZZER_PIN = 23  # GPIO 23 (Pin 16)

# IR Remote Button Codes
# Adjust these codes based on your specific IR remote
IR_CODES = {
    'UP': 0x18,      # Button 2 (↑)
    'LEFT': 0x08,    # Button 4 (←)
    'SELECT': 0x1C,  # Button 5 (OK/Select)
    'RIGHT': 0x5A,   # Button 6 (→)
    'DOWN': 0x52,    # Button 8 (↓)
}

# Game Settings
DIFFICULTY_SPEEDS = {
    'Easy': 300,     # milliseconds (slower)
    'Normal': 200,   # milliseconds
    'Hard': 100,     # milliseconds (faster)
}

# Grid Sizes
SNAKE_GRID_SIZE = 8      # 8x8 grid
TETRIS_GRID_WIDTH = 8    # 8 wide
TETRIS_GRID_HEIGHT = 16  # 16 tall (double height)
