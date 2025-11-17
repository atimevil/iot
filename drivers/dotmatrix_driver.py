"""8x8 Dot Matrix Driver for Raspberry Pi (1088BS+ Direct GPIO Control)"""
import time
import threading

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. Dot Matrix will be simulated.")

from config.pins import DOTMATRIX_ROWS, DOTMATRIX_COLS


class DotMatrix:
    """8x8 LED Dot Matrix Driver for 1088BS+ (Direct GPIO Control)

    1088BS+ uses Row-Anode, Column-Cathode configuration:
    - Row pins: Set HIGH to activate row
    - Column pins: Set LOW to light up LED

    Uses multiplexing to display full 8x8 patterns.
    """

    def __init__(self):
        self.row_pins = DOTMATRIX_ROWS
        self.col_pins = DOTMATRIX_COLS
        self.pattern = [0x00] * 8  # 8 bytes for 8 rows
        self.running = False
        self.refresh_thread = None

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)

            # Setup row pins as OUTPUT (Anode)
            for pin in self.row_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)  # Initially off

            # Setup column pins as OUTPUT (Cathode)
            for pin in self.col_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)  # Initially off (HIGH = off for cathode)

            # Start refresh thread for multiplexing
            self.running = True
            self.refresh_thread = threading.Thread(target=self._refresh_display, daemon=True)
            self.refresh_thread.start()

    def _refresh_display(self):
        """Continuously refresh display using multiplexing"""
        while self.running:
            for row_idx in range(8):
                if not self.running:
                    break

                # Turn off all rows first
                for pin in self.row_pins:
                    GPIO.output(pin, GPIO.LOW)

                # Set column data for this row
                row_data = self.pattern[row_idx]
                for col_idx in range(8):
                    # Bit is 1 = LED on, so set column LOW
                    # Bit is 0 = LED off, so set column HIGH
                    bit = (row_data >> (7 - col_idx)) & 1
                    GPIO.output(self.col_pins[col_idx], GPIO.LOW if bit else GPIO.HIGH)

                # Activate this row
                GPIO.output(self.row_pins[row_idx], GPIO.HIGH)

                # Small delay for persistence of vision (~1ms per row = 125Hz refresh)
                time.sleep(0.001)

    def clear(self):
        """Clear the display"""
        self.pattern = [0x00] * 8

    def display_pattern(self, pattern):
        """Display 8x8 pattern (list of 8 bytes)

        Args:
            pattern: List of 8 bytes, each byte represents a row
                    MSB (bit 7) = leftmost LED, LSB (bit 0) = rightmost LED
        """
        if len(pattern) != 8:
            return

        self.pattern = pattern[:]

        if not GPIO_AVAILABLE:
            self._print_pattern_debug()

    def _print_pattern_debug(self):
        """Print pattern to console for debugging"""
        print("\nDot Matrix Pattern:")
        for row in self.pattern:
            print(''.join(['█' if row & (1 << (7-i)) else '·' for i in range(8)]))

    def display_pixel(self, x, y, state=True):
        """Light up or turn off a single pixel

        Args:
            x: Column position (0-7)
            y: Row position (0-7)
            state: True to turn on, False to turn off
        """
        if 0 <= x < 8 and 0 <= y < 8:
            if state:
                self.pattern[y] |= (1 << (7 - x))
            else:
                self.pattern[y] &= ~(1 << (7 - x))

    def display_snake_segment(self, x, y):
        """Display a single dot for snake game"""
        self.clear()
        if 0 <= x < 8 and 0 <= y < 8:
            self.pattern[y] = 1 << (7 - x)

    def display_tetris_block(self, block_pattern):
        """Display Tetris block

        Args:
            block_pattern: List of 8 bytes representing the Tetris piece
        """
        self.display_pattern(block_pattern)

    def display_flappy_bird(self, bird_y, pipe_x, pipe_gap_y):
        """Display Flappy Bird game state

        Args:
            bird_y: Bird vertical position (0-7)
            pipe_x: Pipe horizontal position (0-7)
            pipe_gap_y: Top of the gap in the pipe (0-7)
        """
        pattern = [0] * 8

        # Draw bird at column 2
        if 0 <= bird_y < 8:
            pattern[bird_y] |= 0b00100000  # Bird at column 2

        # Draw pipe
        if 0 <= pipe_x < 8:
            for y in range(8):
                # Draw pipe except for gap (gap is 3 pixels high)
                if y < pipe_gap_y or y > pipe_gap_y + 2:
                    pattern[y] |= (1 << (7 - pipe_x))

        self.display_pattern(pattern)

    def display_number(self, num):
        """Display a single digit number (0-9) on the matrix

        Useful for showing scores or countdowns
        """
        # Simple 5x7 font patterns for digits 0-9
        digits = {
            0: [0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
            1: [0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x7E, 0x00],
            2: [0x3C, 0x66, 0x06, 0x0C, 0x18, 0x30, 0x7E, 0x00],
            3: [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00],
            4: [0x0C, 0x1C, 0x2C, 0x4C, 0x7E, 0x0C, 0x0C, 0x00],
            5: [0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00],
            6: [0x3C, 0x60, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00],
            7: [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x30, 0x30, 0x00],
            8: [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00],
            9: [0x3C, 0x66, 0x66, 0x3E, 0x06, 0x06, 0x3C, 0x00],
        }

        if num in digits:
            self.display_pattern(digits[num])
        else:
            self.clear()

    def display_text_scroll(self, text):
        """Scroll text across the display (placeholder for future implementation)"""
        # This would require character font definitions and scrolling logic
        pass

    def set_brightness(self, level):
        """Adjust brightness by controlling refresh timing

        Args:
            level: Brightness level 0.0 (off) to 1.0 (max)
        """
        # For software PWM, would adjust duty cycle in refresh loop
        # Current implementation: full brightness always
        pass

    def cleanup(self):
        """Cleanup GPIO and stop refresh thread"""
        self.running = False

        if self.refresh_thread:
            self.refresh_thread.join(timeout=1.0)

        if GPIO_AVAILABLE:
            # Turn off all LEDs
            for pin in self.row_pins:
                GPIO.output(pin, GPIO.LOW)
            for pin in self.col_pins:
                GPIO.output(pin, GPIO.HIGH)

            # Cleanup GPIO
            GPIO.cleanup(self.row_pins + self.col_pins)
