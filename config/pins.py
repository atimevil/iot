# Pin Configuration for Raspberry Pi 4 + Arduino Full Kit EK100

# I2C LCD (16x2)
LCD_I2C_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2

# IR Receiver
IR_PIN = 18

# Buzzer
BUZZER_PIN = 23

# LEDs
LED_RED_PIN = 17
LED_GREEN_PIN = 27
LED_BLUE_PIN = 22

# 7-Segment Display (FND) - Using shift register
FND_DATA_PIN = 24
FND_LATCH_PIN = 25
FND_CLOCK_PIN = 8

# Dot Matrix (8x8) - MAX7219
DOTMATRIX_DIN = 10
DOTMATRIX_CS = 9
DOTMATRIX_CLK = 11

# IR Remote Button Codes (adjust based on your remote)
IR_CODES = {
    'UP': 0x18,      # Button 2
    'DOWN': 0x52,    # Button 8
    'LEFT': 0x08,    # Button 4
    'RIGHT': 0x5A,   # Button 6
    'SELECT': 0x1C,  # Button 5
    'MENU': 0x45,    # Menu button
}

# Game Settings
DIFFICULTY_SPEEDS = {
    'Easy': 200,    # milliseconds
    'Normal': 150,
    'Hard': 100
}
