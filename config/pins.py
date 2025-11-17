# Pin Configuration for Raspberry Pi 4 + Arduino Full Kit EK100

# I2C LCD (16x2)
LCD_I2C_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2

# IR Receiver
IR_PIN = 18

# Buzzer
BUZZER_PIN = 23

# LEDs - DISABLED (웹 화면에서 시각 효과 표시)
# LED_RED_PIN = 17
# LED_GREEN_PIN = 27
# LED_BLUE_PIN = 22
LED_ENABLED = False

# 7-Segment Display (FND) - DISABLED (웹 화면에서 점수 표시)
# FND_DATA_PIN = 24
# FND_LATCH_PIN = 25
# FND_CLOCK_PIN = 8
FND_ENABLED = False

# Dot Matrix (8x8) - 1088BS+ Direct GPIO Control
# 16-pin direct connection (Row 8 + Column 8)
DOTMATRIX_ENABLED = True

# Row pins (Anode, 양극) - 행 선택
DOTMATRIX_ROWS = [4, 17, 27, 22, 5, 6, 13, 19]  # Row 0-7

# Column pins (Cathode, 음극) - 열 데이터
DOTMATRIX_COLS = [26, 12, 16, 20, 21, 7, 8, 25]  # Col 0-7

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
