"""LED Driver for Raspberry Pi"""
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. LED will be simulated.")

from config.pins import LED_RED_PIN, LED_GREEN_PIN, LED_BLUE_PIN


class LED:
    """RGB LED Driver"""

    def __init__(self, red_pin=LED_RED_PIN, green_pin=LED_GREEN_PIN, blue_pin=LED_BLUE_PIN):
        self.pins = {
            'red': red_pin,
            'green': green_pin,
            'blue': blue_pin
        }

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            for pin in self.pins.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

    def on(self, color='red'):
        """Turn on specific color LED"""
        if GPIO_AVAILABLE and color in self.pins:
            GPIO.output(self.pins[color], GPIO.HIGH)
        else:
            print(f"LED {color.upper()} ON")

    def off(self, color='red'):
        """Turn off specific color LED"""
        if GPIO_AVAILABLE and color in self.pins:
            GPIO.output(self.pins[color], GPIO.LOW)
        else:
            print(f"LED {color.upper()} OFF")

    def all_off(self):
        """Turn off all LEDs"""
        for color in self.pins.keys():
            self.off(color)

    def blink(self, color='red', times=3, interval=0.2):
        """Blink LED"""
        for _ in range(times):
            self.on(color)
            time.sleep(interval)
            self.off(color)
            time.sleep(interval)

    def game_start_effect(self):
        """LED effect for game start"""
        colors = ['red', 'green', 'blue']
        for color in colors:
            self.on(color)
            time.sleep(0.1)
            self.off(color)

    def game_over_effect(self):
        """LED effect for game over"""
        self.blink('red', times=5, interval=0.15)

    def cleanup(self):
        """Cleanup GPIO"""
        self.all_off()
        if GPIO_AVAILABLE:
            for pin in self.pins.values():
                GPIO.cleanup(pin)
