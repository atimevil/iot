"""LED Driver for Raspberry Pi - DISABLED (Visual effects shown on web)"""
import time

from config.pins import LED_ENABLED


class LED:
    """RGB LED Driver - DISABLED

    This hardware component has been disabled.
    Visual effects are handled by the web interface instead.
    """

    def __init__(self):
        self.enabled = LED_ENABLED

        if not self.enabled:
            print("INFO: LED disabled - using web display for visual effects")

    def on(self, color='red'):
        """Turn on specific color LED - No-op when disabled"""
        if not self.enabled:
            return
        print(f"LED {color.upper()} ON")

    def off(self, color='red'):
        """Turn off specific color LED - No-op when disabled"""
        if not self.enabled:
            return
        print(f"LED {color.upper()} OFF")

    def all_off(self):
        """Turn off all LEDs - No-op when disabled"""
        pass

    def blink(self, color='red', times=3, interval=0.2):
        """Blink LED - No-op when disabled"""
        pass

    def game_start_effect(self):
        """LED effect for game start - No-op when disabled"""
        pass

    def game_over_effect(self):
        """LED effect for game over - No-op when disabled"""
        pass

    def cleanup(self):
        """Cleanup - No-op when disabled"""
        pass
