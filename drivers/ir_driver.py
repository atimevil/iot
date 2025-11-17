"""IR Remote Control Driver for Raspberry Pi"""
import threading
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. IR will be simulated.")

try:
    import lirc
    LIRC_AVAILABLE = True
except ImportError:
    LIRC_AVAILABLE = False
    print("Warning: python-lirc not available. Using fallback IR reading.")

from config.pins import IR_PIN, IR_CODES


class IRRemote:
    """IR Remote Control Driver with LIRC support"""

    def __init__(self, pin=IR_PIN, callback=None):
        self.pin = pin
        self.callback = callback
        self.last_code = None
        self.running = False
        self.reader_thread = None

        # Try LIRC first (most reliable)
        if LIRC_AVAILABLE:
            try:
                self.lirc_client = lirc.Client()
                self.use_lirc = True
                print("[IR] Using LIRC for IR remote")
            except Exception as e:
                print(f"[IR] LIRC initialization failed: {e}")
                self.use_lirc = False
        else:
            self.use_lirc = False

        # Fallback to GPIO
        if not self.use_lirc and GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            print("[IR] Using GPIO fallback for IR remote")

    def start_reading(self, callback):
        """Start reading IR codes in background thread"""
        self.callback = callback
        self.running = True

        if self.use_lirc:
            self.reader_thread = threading.Thread(target=self._lirc_reader_loop, daemon=True)
        else:
            self.reader_thread = threading.Thread(target=self._gpio_reader_loop, daemon=True)

        self.reader_thread.start()
        print("[IR] IR remote reader started")

    def _lirc_reader_loop(self):
        """Read IR codes using LIRC (recommended method)"""
        while self.running:
            try:
                # Read IR code from LIRC
                code = self.lirc_client.read(timeout=0.1)
                if code:
                    button_name = self.get_button_name_from_lirc(code)
                    if button_name and self.callback:
                        self.callback(button_name)
            except Exception as e:
                print(f"[IR] LIRC read error: {e}")
                time.sleep(0.1)

    def _gpio_reader_loop(self):
        """Read IR codes using GPIO (fallback method)"""
        # This is a simplified IR reader
        # For production, LIRC is strongly recommended
        pulse_times = []
        last_state = 1

        while self.running:
            try:
                if GPIO_AVAILABLE:
                    current_state = GPIO.input(self.pin)

                    if current_state != last_state:
                        pulse_times.append(time.time())
                        last_state = current_state

                        # Decode after receiving enough pulses
                        if len(pulse_times) > 32:
                            code = self._decode_nec_protocol(pulse_times)
                            if code:
                                button_name = self.get_button_name(code)
                                if button_name and self.callback:
                                    self.callback(button_name)
                            pulse_times = []

                time.sleep(0.0001)  # 100 microseconds
            except Exception as e:
                print(f"[IR] GPIO read error: {e}")
                time.sleep(0.1)

    def _decode_nec_protocol(self, pulse_times):
        """Decode NEC IR protocol from pulse times"""
        # Simplified NEC decoder
        # This is a basic implementation - LIRC is more reliable
        try:
            if len(pulse_times) < 32:
                return None

            # Convert pulse times to bits
            bits = []
            for i in range(1, len(pulse_times) - 1, 2):
                pulse_width = pulse_times[i + 1] - pulse_times[i]
                bits.append(1 if pulse_width > 0.001 else 0)

            # Extract command byte (NEC protocol)
            if len(bits) >= 32:
                command = 0
                for i in range(8):
                    command |= (bits[16 + i] << i)
                return command
        except:
            pass

        return None

    def get_button_name(self, code):
        """Convert IR code to button name"""
        for name, ir_code in IR_CODES.items():
            if ir_code == code:
                return name
        return None

    def get_button_name_from_lirc(self, lirc_code):
        """Convert LIRC code string to button name"""
        # LIRC returns strings like "KEY_UP", "KEY_DOWN", etc.
        # Map them to our button names
        lirc_to_button = {
            'KEY_UP': 'UP',
            'KEY_2': 'UP',
            'KEY_DOWN': 'DOWN',
            'KEY_8': 'DOWN',
            'KEY_LEFT': 'LEFT',
            'KEY_4': 'LEFT',
            'KEY_RIGHT': 'RIGHT',
            'KEY_6': 'RIGHT',
            'KEY_OK': 'SELECT',
            'KEY_5': 'SELECT',
            'KEY_ENTER': 'SELECT',
        }

        return lirc_to_button.get(lirc_code, None)

    def stop_reading(self):
        """Stop reading IR codes"""
        self.running = False
        if self.reader_thread:
            self.reader_thread.join(timeout=2.0)
        print("[IR] IR remote reader stopped")

    def cleanup(self):
        """Cleanup resources"""
        self.stop_reading()

        if self.use_lirc:
            try:
                self.lirc_client.close()
            except:
                pass

        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.pin)
            except:
                pass
