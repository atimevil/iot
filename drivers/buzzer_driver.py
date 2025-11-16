"""Buzzer Driver for Raspberry Pi"""
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. Buzzer will be simulated.")

from config.pins import BUZZER_PIN


class Buzzer:
    """Buzzer Driver"""

    def __init__(self, pin=BUZZER_PIN):
        self.pin = pin

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pin, 1000)
        else:
            self.pwm = None

    def beep(self, duration=0.1):
        """Simple beep"""
        if self.pwm:
            self.pwm.start(50)
            time.sleep(duration)
            self.pwm.stop()
        else:
            print(f"BEEP ({duration}s)")

    def play_tone(self, frequency, duration):
        """Play specific tone"""
        if self.pwm:
            self.pwm.ChangeFrequency(frequency)
            self.pwm.start(50)
            time.sleep(duration)
            self.pwm.stop()
        else:
            print(f"TONE: {frequency}Hz for {duration}s")

    def game_over_sound(self):
        """Play game over sound"""
        tones = [(400, 0.2), (300, 0.2), (200, 0.3)]
        for freq, duration in tones:
            self.play_tone(freq, duration)
            time.sleep(0.05)

    def score_sound(self):
        """Play score increase sound"""
        self.play_tone(800, 0.1)

    def cleanup(self):
        """Cleanup GPIO"""
        if self.pwm:
            self.pwm.stop()
        if GPIO_AVAILABLE:
            GPIO.cleanup(self.pin)
