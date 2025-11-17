"""7-Segment FND Driver for Raspberry Pi - DISABLED (Score shown on web)"""

from config.pins import FND_ENABLED


class FND:
    """4-Digit 7-Segment Display Driver - DISABLED

    This hardware component has been disabled.
    Score display is handled by the web interface instead.
    """

    def __init__(self):
        self.score = 0
        self.enabled = FND_ENABLED

        if not self.enabled:
            print("INFO: FND disabled - using web display for scores")

    def display_digit(self, digit):
        """Display single digit - No-op when disabled"""
        pass

    def display_number(self, number):
        """Display 4-digit number - No-op when disabled"""
        if not self.enabled:
            return
        # Would display on hardware if enabled

    def set_score(self, score):
        """Set and display score"""
        self.score = score
        if not self.enabled:
            # Score is displayed on web interface instead
            return
        self.display_number(score)

    def increment_score(self, amount=1):
        """Increment score"""
        self.score += amount
        if not self.enabled:
            return
        self.display_number(self.score)

    def reset_score(self):
        """Reset score to 0"""
        self.score = 0
        if not self.enabled:
            return
        self.display_number(0)

    def cleanup(self):
        """Cleanup - No-op when disabled"""
        pass
