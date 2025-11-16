"""7-Segment FND Driver for Raspberry Pi"""
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. FND will be simulated.")

from config.pins import FND_DATA_PIN, FND_LATCH_PIN, FND_CLOCK_PIN


class FND:
    """4-Digit 7-Segment Display Driver using Shift Register"""

    # 7-segment digit patterns (0-9)
    DIGITS = [
        0b11111100,  # 0
        0b01100000,  # 1
        0b11011010,  # 2
        0b11110010,  # 3
        0b01100110,  # 4
        0b10110110,  # 5
        0b10111110,  # 6
        0b11100000,  # 7
        0b11111110,  # 8
        0b11110110,  # 9
    ]

    def __init__(self, data_pin=FND_DATA_PIN, latch_pin=FND_LATCH_PIN, clock_pin=FND_CLOCK_PIN):
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        self.score = 0

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.data_pin, GPIO.OUT)
            GPIO.setup(self.latch_pin, GPIO.OUT)
            GPIO.setup(self.clock_pin, GPIO.OUT)

    def shift_out(self, data):
        """Shift out data to shift register"""
        if not GPIO_AVAILABLE:
            return

        GPIO.output(self.latch_pin, GPIO.LOW)

        for i in range(7, -1, -1):
            GPIO.output(self.clock_pin, GPIO.LOW)
            bit = (data >> i) & 1
            GPIO.output(self.data_pin, bit)
            GPIO.output(self.clock_pin, GPIO.HIGH)

        GPIO.output(self.latch_pin, GPIO.HIGH)

    def display_digit(self, digit):
        """Display single digit"""
        if 0 <= digit <= 9:
            self.shift_out(self.DIGITS[digit])
        else:
            self.shift_out(0)

    def display_number(self, number):
        """Display 4-digit number"""
        if number > 9999:
            number = 9999
        elif number < 0:
            number = 0

        digits = [
            (number // 1000) % 10,
            (number // 100) % 10,
            (number // 10) % 10,
            number % 10
        ]

        # In real implementation, would multiplex 4 digits
        # For now, just display the rightmost digit
        self.display_digit(digits[3])

        if not GPIO_AVAILABLE:
            print(f"FND Display: {number:04d}")

    def set_score(self, score):
        """Set and display score"""
        self.score = score
        self.display_number(score)

    def increment_score(self, amount=1):
        """Increment score"""
        self.score += amount
        self.display_number(self.score)

    def reset_score(self):
        """Reset score to 0"""
        self.score = 0
        self.display_number(0)

    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE:
            GPIO.cleanup([self.data_pin, self.latch_pin, self.clock_pin])
