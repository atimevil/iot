"""I2C LCD 16x2 Driver for Raspberry Pi"""
import time

try:
    import smbus
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False
    print("Warning: smbus not available. LCD will be simulated.")

from config.pins import LCD_I2C_ADDRESS, LCD_COLS, LCD_ROWS


class LCD:
    """16x2 I2C LCD Display Driver"""

    # LCD Commands
    LCD_CMD = 0
    LCD_CHR = 1
    LCD_LINE_1 = 0x80
    LCD_LINE_2 = 0xC0
    LCD_BACKLIGHT = 0x08
    ENABLE = 0b00000100

    def __init__(self, address=LCD_I2C_ADDRESS):
        self.address = address
        self.bus = smbus.SMBus(1) if I2C_AVAILABLE else None
        if self.bus:
            self.init_display()

    def init_display(self):
        """Initialize the LCD display"""
        if not self.bus:
            return

        self.write_byte(0x33, self.LCD_CMD)
        self.write_byte(0x32, self.LCD_CMD)
        self.write_byte(0x06, self.LCD_CMD)
        self.write_byte(0x0C, self.LCD_CMD)
        self.write_byte(0x28, self.LCD_CMD)
        self.write_byte(0x01, self.LCD_CMD)
        time.sleep(0.0005)

    def write_byte(self, bits, mode):
        """Write a byte to the LCD"""
        if not self.bus:
            return

        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | self.LCD_BACKLIGHT

        self.bus.write_byte(self.address, bits_high)
        self.toggle_enable(bits_high)

        self.bus.write_byte(self.address, bits_low)
        self.toggle_enable(bits_low)

    def toggle_enable(self, bits):
        """Toggle enable bit"""
        if not self.bus:
            return

        time.sleep(0.0005)
        self.bus.write_byte(self.address, (bits | self.ENABLE))
        time.sleep(0.0005)
        self.bus.write_byte(self.address, (bits & ~self.ENABLE))
        time.sleep(0.0005)

    def clear(self):
        """Clear the display"""
        self.write_byte(0x01, self.LCD_CMD)

    def display_text(self, text, line=1):
        """Display text on specified line (1 or 2)"""
        if line == 1:
            self.write_byte(self.LCD_LINE_1, self.LCD_CMD)
        else:
            self.write_byte(self.LCD_LINE_2, self.LCD_CMD)

        text = text.ljust(LCD_COLS)[:LCD_COLS]
        for char in text:
            self.write_byte(ord(char), self.LCD_CHR)

    def display_two_lines(self, line1, line2):
        """Display text on both lines"""
        self.clear()
        self.display_text(line1, 1)
        self.display_text(line2, 2)
