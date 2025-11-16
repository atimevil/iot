"""8x8 Dot Matrix Driver for Raspberry Pi (MAX7219)"""
import time

try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False
    print("Warning: spidev not available. Dot Matrix will be simulated.")

from config.pins import DOTMATRIX_DIN, DOTMATRIX_CS, DOTMATRIX_CLK


class DotMatrix:
    """8x8 LED Dot Matrix Driver using MAX7219"""

    # MAX7219 Registers
    REG_NOOP = 0x00
    REG_DIGIT0 = 0x01
    REG_DIGIT7 = 0x08
    REG_DECODEMODE = 0x09
    REG_INTENSITY = 0x0A
    REG_SCANLIMIT = 0x0B
    REG_SHUTDOWN = 0x0C
    REG_DISPLAYTEST = 0x0F

    def __init__(self):
        self.spi = None

        if SPI_AVAILABLE:
            self.spi = spidev.SpiDev()
            try:
                self.spi.open(0, 0)
                self.spi.max_speed_hz = 1000000
                self.init_matrix()
            except:
                self.spi = None
                print("Warning: Could not initialize SPI for Dot Matrix")

    def init_matrix(self):
        """Initialize the MAX7219"""
        if not self.spi:
            return

        self.write_register(self.REG_SHUTDOWN, 0x01)      # Normal operation
        self.write_register(self.REG_DECODEMODE, 0x00)    # No decode
        self.write_register(self.REG_SCANLIMIT, 0x07)     # All 8 digits
        self.write_register(self.REG_INTENSITY, 0x08)     # Medium brightness
        self.write_register(self.REG_DISPLAYTEST, 0x00)   # Normal operation
        self.clear()

    def write_register(self, register, data):
        """Write to MAX7219 register"""
        if self.spi:
            self.spi.xfer2([register, data])

    def clear(self):
        """Clear the display"""
        for i in range(8):
            self.write_register(self.REG_DIGIT0 + i, 0x00)

    def display_pattern(self, pattern):
        """Display 8x8 pattern (list of 8 bytes)"""
        if len(pattern) != 8:
            return

        if self.spi:
            for row in range(8):
                self.write_register(self.REG_DIGIT0 + row, pattern[row])
        else:
            print("Dot Matrix Pattern:")
            for row in pattern:
                print(''.join(['█' if row & (1 << (7-i)) else '·' for i in range(8)]))

    def display_snake_segment(self, x, y):
        """Display a single dot for snake"""
        pattern = [0] * 8
        if 0 <= y < 8:
            pattern[y] = 1 << (7 - x) if 0 <= x < 8 else 0
        self.display_pattern(pattern)

    def display_tetris_block(self, block_pattern):
        """Display Tetris block"""
        self.display_pattern(block_pattern)

    def display_flappy_bird(self, bird_y, pipe_x, pipe_gap_y):
        """Display Flappy Bird game state"""
        pattern = [0] * 8

        # Draw bird
        if 0 <= bird_y < 8:
            pattern[bird_y] |= 0b00001000

        # Draw pipe
        if 0 <= pipe_x < 8:
            for y in range(8):
                if y < pipe_gap_y or y > pipe_gap_y + 2:
                    pattern[y] |= (1 << (7 - pipe_x))

        self.display_pattern(pattern)

    def cleanup(self):
        """Cleanup SPI"""
        if self.spi:
            self.clear()
            self.spi.close()
