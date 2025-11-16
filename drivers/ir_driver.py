"""IR Remote Control Driver for Raspberry Pi"""
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. IR will be simulated.")

from config.pins import IR_PIN, IR_CODES


class IRRemote:
    """IR Remote Control Driver"""

    def __init__(self, pin=IR_PIN, callback=None):
        self.pin = pin
        self.callback = callback
        self.last_code = None

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)

    def read_code(self):
        """Read IR code (simplified - use LIRC for production)"""
        # This is a simplified version
        # For production, use python-lirc library
        return self.last_code

    def get_button_name(self, code):
        """Convert IR code to button name"""
        for name, ir_code in IR_CODES.items():
            if ir_code == code:
                return name
        return None

    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE:
            GPIO.cleanup(self.pin)
