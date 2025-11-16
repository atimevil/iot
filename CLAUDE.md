# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raspberry Pi 4 Game Console** - IoT System Application Team Project (Team 5)

A game console system using Raspberry Pi 4 and Arduino Full Kit EK100, featuring three classic games playable through a web browser with hardware integration (LCD, Dot Matrix, IR Remote, Buzzer, LED, FND).

## Technology Stack

- **Platform**: Raspberry Pi 4
- **Hardware Kit**: Arduino Full Kit EK100
- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5 Canvas + JavaScript + WebSocket
- **Hardware Control**: RPi.GPIO, smbus2, spidev
- **Communication**: I2C (LCD), SPI (Dot Matrix), GPIO (IR, Buzzer, LED, FND)

## Project Structure

```
iot/
├── config/           # Hardware pin configurations
├── drivers/          # Hardware device drivers
├── games/            # Game logic modules
└── web/             # Flask web application
    ├── app.py       # Main application
    └── templates/   # HTML game interfaces
```

## Development Commands

### Run the Application
```bash
cd web
python3 app.py
```
Access at `http://[raspberry-pi-ip]:5000`

### Test Hardware Drivers
```bash
# Test LCD
python3 -c "from drivers.lcd_driver import LCD; lcd = LCD(); lcd.display_two_lines('Test', 'LCD')"

# Test Buzzer
python3 -c "from drivers.buzzer_driver import Buzzer; b = Buzzer(); b.beep(0.5)"

# Test LED
python3 -c "from drivers.led_driver import LED; led = LED(); led.game_start_effect()"
```

### Check I2C Devices
```bash
sudo i2cdetect -y 1
```

### GPIO Permissions
```bash
sudo usermod -a -G gpio,i2c,spi $USER
# Logout and login required
```

## Architecture

### Hardware Layer
- **drivers/** modules provide abstraction for hardware components
- Each driver handles initialization, control, and cleanup
- Fallback to simulation mode when hardware is unavailable

### Game Logic Layer
- **games/** modules contain pure game logic
- Thread-safe implementation using locks
- Independent of display mechanism (web canvas or hardware)
- Each game exposes `get_state()`, `update()`, `reset()` methods

### Web Layer
- Flask serves HTML5 game interfaces
- Flask-SocketIO provides real-time bidirectional communication
- Game state broadcast at 20 FPS to all connected clients
- Client-side Canvas rendering with keyboard/IR remote input

### Communication Flow
```
User Input (Web/IR) → Flask-SocketIO → Game Logic →
Hardware Feedback (LCD/Buzzer/LED/FND) + Web State Update → Canvas Rendering
```

## Key Components

### Pin Configuration (`config/pins.py`)
- Centralized GPIO pin assignments
- IR remote button code mappings
- Difficulty speed settings

### Hardware Drivers
- **LCD (I2C)**: 16x2 character display
- **Dot Matrix (SPI)**: 8x8 LED matrix with MAX7219
- **IR Remote (GPIO)**: Infrared receiver for game control
- **FND (Shift Register)**: 4-digit 7-segment score display
- **Buzzer (PWM)**: Audio feedback with tone generation
- **LED (GPIO)**: RGB LED for visual effects

### Game Implementations

**Snake Game** (`games/snake_game.py`)
- Grid-based movement with direction queuing
- Collision detection (wall, self)
- Food generation and score tracking
- Thread-safe state updates

**Tetris Game** (`games/tetris_game.py`)
- Tetromino shapes and rotation
- Line clearing and score calculation
- Collision detection and piece locking
- Game over detection at spawn

**Flappy Bird Game** (`games/flappy_bird_game.py`)
- Physics-based bird movement (gravity, velocity)
- Procedural pipe generation
- Collision detection (pipe, ground, ceiling)
- Score on pipe passage

### WebSocket Events
- `start_game`: Initialize game with difficulty
- `game_input`: Handle keyboard/IR input
- `reset_game`: Restart current game
- `stop_game`: Stop game and cleanup
- `game_state`: Broadcast current game state (server → client)

## Hardware Configuration

### I2C LCD Address
Default: `0x27` - Change in `config/pins.py` if different
Check with: `sudo i2cdetect -y 1`

### IR Remote Codes
Codes in `config/pins.py` are for standard remote
Capture your remote codes and update accordingly

### Difficulty Speeds
Adjust timing in `DIFFICULTY_SPEEDS` dict for game balance

## Common Issues

**GPIO Permission Denied**
- Add user to gpio/i2c/spi groups
- Use `sudo` for testing only

**I2C Device Not Found**
- Enable I2C in `raspi-config`
- Check wiring and power
- Verify address with `i2cdetect`

**SPI Not Working**
- Enable SPI in `raspi-config`
- Check MOSI/MISO/SCLK connections
- Verify MAX7219 chip power

**Port 5000 Already in Use**
- Kill existing process: `sudo lsof -i :5000`
- Or change port in `app.py`

## Code Style

- Hardware drivers include simulation fallback
- All GPIO cleanup in `cleanup()` methods
- Thread-safe game logic using locks
- WebSocket for all client-server communication
- Canvas rendering on client, state on server

## Testing Strategy

### Unit Testing
Test individual game logic without hardware:
```python
game = SnakeGame()
game.change_direction('RIGHT')
game.update()
assert game.snake[0] != game.snake[1]
```

### Hardware Testing
Test each driver independently before integration

### Integration Testing
Run full game loop with hardware feedback verification

## Pin Reference

| Component | GPIO Pin | BCM # | Description |
|-----------|----------|-------|-------------|
| LCD SDA | Pin 3 | GPIO 2 | I2C Data |
| LCD SCL | Pin 5 | GPIO 3 | I2C Clock |
| IR Receiver | Pin 12 | GPIO 18 | IR Signal |
| Buzzer | Pin 16 | GPIO 23 | PWM Output |
| LED Red | Pin 11 | GPIO 17 | Red LED |
| LED Green | Pin 13 | GPIO 27 | Green LED |
| LED Blue | Pin 15 | GPIO 22 | Blue LED |
| FND Data | Pin 18 | GPIO 24 | Shift Register Data |
| FND Latch | Pin 22 | GPIO 25 | Shift Register Latch |
| FND Clock | Pin 24 | GPIO 8 | Shift Register Clock |
| Matrix DIN | Pin 19 | GPIO 10 | SPI MOSI |
| Matrix CS | Pin 21 | GPIO 9 | SPI Chip Select |
| Matrix CLK | Pin 23 | GPIO 11 | SPI Clock |

## Team

- Team Leader: 김태형 (Development)
- Team Member: 김지환 (Presentation)
- Team Member: 나민서 (Planning)
- Supervisor: 송기범 교수님
