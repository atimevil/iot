# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raspberry Pi 4 Game Console** - IoT System Application Team Project (Team 5)

A game console system using Raspberry Pi 4 and Arduino Full Kit EK100, featuring three classic games playable through a web browser with hardware integration (LCD, Dot Matrix, IR Remote, Buzzer, LED, FND).

## Technology Stack

- **Platform**: Raspberry Pi 4
- **Hardware Kit**: Arduino Full Kit EK100 + 1088BS+ Dot Matrix + 3431AS-1 FND
- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5 Canvas + JavaScript + WebSocket
- **Hardware Control**: RPi.GPIO, smbus2
- **Communication**: I2C (LCD), GPIO (Dot Matrix, IR, Buzzer)

## Project Structure

```
iot/
├── config/           # Hardware pin configurations
├── drivers/          # Hardware device drivers
├── database/         # SQLite database and models
│   ├── models.py    # Database interface
│   └── game_scores.db  # Score database (auto-generated)
├── games/            # Game logic modules
│   ├── snake_game.py
│   ├── tetris_game.py
│   └── suika_game.py
└── web/             # Flask web application
    ├── app.py       # Main application
    └── templates/   # HTML game interfaces
        ├── index.html
        ├── snake.html
        ├── tetris.html
        ├── suika.html
        └── scoreboard.html
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

# Test Dot Matrix (displays number 8)
python3 -c "from drivers.dotmatrix_driver import DotMatrix; dm = DotMatrix(); dm.display_number(8); import time; time.sleep(3); dm.cleanup()"

# Test individual pixel
python3 -c "from drivers.dotmatrix_driver import DotMatrix; dm = DotMatrix(); dm.display_pixel(4, 4); import time; time.sleep(3); dm.cleanup()"
```

### Check I2C Devices
```bash
sudo i2cdetect -y 1
```

### Debug Dot Matrix
```python
# Test all rows
from drivers.dotmatrix_driver import DotMatrix
dm = DotMatrix()
for row in range(8):
    dm.pattern = [0xFF if i == row else 0x00 for i in range(8)]
    import time; time.sleep(1)
dm.cleanup()

# Test all columns
for col in range(8):
    dm.pattern = [1 << (7-col)] * 8
    import time; time.sleep(1)
dm.cleanup()
```

### GPIO Permissions
```bash
sudo usermod -a -G gpio,i2c $USER
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
- Nickname input modal before game start (all games)
- Auto-save score to database on game over

### Database Layer
- **SQLite**: Lightweight database for score persistence
- **models.py**: Database interface with CRUD operations
- **Auto-initialization**: Database created on first run
- **Score tracking**: Player name, game, score, difficulty, timestamp

### Communication Flow
```
1. Game Start Flow:
   User clicks Start → Nickname Modal → Enter Name →
   start_game event → Game initialized with player_name

2. Gameplay Flow:
   User Input (Web/IR) → game_input event → Game Logic Update →
   game_state broadcast (20 FPS) → Canvas Rendering

3. Game Over Flow:
   Game Over Detected → save_score event →
   Database Save → Scoreboard Update
```

## Key Components

### Database (`database/models.py`)
- **DatabaseManager**: Singleton class for database operations
- **Schema**: scores table (id, game, player_name, score, difficulty, timestamp)
- **Methods**:
  - `add_score(game, player_name, score, difficulty)`: Insert new score
  - `get_top_scores(game, limit, difficulty)`: Get top N scores for a game
  - `get_all_top_scores(limit)`: Get top N scores across all games
  - `get_game_stats(game)`: Get statistics for a game
  - `get_all_stats()`: Get overall statistics

### Pin Configuration (`config/pins.py`)
- Centralized GPIO pin assignments
- IR remote button code mappings
- Difficulty speed settings

### Hardware Drivers
- **LCD (I2C)**: 16x2 character display
- **Dot Matrix (GPIO Direct)**: 1088BS+ 8x8 LED matrix with direct GPIO control (16 pins)
- **IR Remote (GPIO)**: Infrared receiver for game control
- **Buzzer (PWM)**: Audio feedback with tone generation
- **FND (DISABLED)**: Score displayed on web interface
- **LED (DISABLED)**: Visual effects shown on web interface

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

**Suika Game** (`games/suika_game.py`)
- Physics-based fruit merging using Pymunk engine
- 10 fruit types (cherry → watermelon)
- Gravity and collision simulation
- Merge detection and scoring system
- Game over when fruits overflow danger line

### WebSocket Events

**Client → Server:**
- `start_game`: Initialize game with difficulty and player name
  - Parameters: `{game, difficulty, player_name}`
- `game_input`: Handle keyboard/IR input
  - Parameters: `{game, action}`
- `reset_game`: Restart current game
- `stop_game`: Stop game and cleanup
- `save_score`: Save score to database
  - Parameters: `{game, player_name, score, difficulty}`

**Server → Client:**
- `game_state`: Broadcast current game state (20 FPS)
- `game_started`: Confirm game initialization
- `game_reset`: Confirm game reset
- `game_stopped`: Confirm game stopped with final score
- `score_saved`: Confirm score saved to database
- `error`: Error message

## Hardware Configuration

### I2C LCD Address
Default: `0x27` - Change in `config/pins.py` if different
Check with: `sudo i2cdetect -y 1`

### Dot Matrix 1088BS+ Wiring
**Connection Type**: Row-Anode, Column-Cathode
- **Row Pins (HIGH = activate row)**: Connect to GPIO 4, 17, 27, 22, 5, 6, 13, 19
- **Column Pins (LOW = LED on)**: Connect to GPIO 26, 12, 16, 20, 21, 7, 8, 25
- **Multiplexing**: Controlled via background thread at 125Hz refresh rate
- **Brightness**: Software-controlled via duty cycle (future enhancement)

### IR Remote Codes
Codes in `config/pins.py` are for standard remote
Capture your remote codes and update accordingly

### Difficulty Speeds
Adjust timing in `DIFFICULTY_SPEEDS` dict for game balance

### Disabled Hardware
- **LED RGB**: Code remains but does nothing (LED_ENABLED = False)
- **FND 7-Segment**: Code remains but does nothing (FND_ENABLED = False)
- Scores and visual effects displayed on web interface instead

## Common Issues

**GPIO Permission Denied**
- Add user to gpio/i2c groups: `sudo usermod -a -G gpio,i2c $USER`
- Logout and login required
- Use `sudo` for testing only

**I2C Device Not Found**
- Enable I2C in `raspi-config`
- Check wiring and power
- Verify address with `i2cdetect -y 1`

**Dot Matrix Not Displaying Correctly**
- Check all 16 pin connections (8 rows + 8 columns)
- Verify Row pins are connected to correct GPIO (Anode)
- Verify Column pins are connected to correct GPIO (Cathode)
- Test individual pixels using `display_pixel(x, y)` method
- Check refresh thread is running (daemon thread)

**Dot Matrix Shows Ghosting/Dim LEDs**
- Increase refresh rate (decrease sleep time in `_refresh_display`)
- Check power supply can handle all LEDs simultaneously
- Verify row activation timing

**Port 5000 Already in Use**
- Kill existing process: `sudo lsof -i :5000`
- Or change port in `app.py`

**Score Not Showing on Web**
- FND is disabled, score shows in web interface only
- Check browser console for WebSocket errors
- Verify `game_state` event includes score field

**Nickname Not Required**
- All games now require nickname input before starting
- Nickname modal appears when clicking "▶️ 시작" button
- Press Enter or click "시작" to confirm nickname

**Score Not Saving to Database**
- Check database file exists: `database/game_scores.db`
- Verify `save_score` event is emitted on game over
- Check player_name is not empty
- Review Flask console for database errors

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

### Active Components

| Component | GPIO Pin (BCM) | Description |
|-----------|----------------|-------------|
| LCD SDA | GPIO 2 | I2C Data |
| LCD SCL | GPIO 3 | I2C Clock |
| IR Receiver | GPIO 18 | IR Signal Input |
| Buzzer | GPIO 23 | PWM Audio Output |

### Dot Matrix 1088BS+ (16 pins)

**Row Pins (Anode, +)**
| Row | GPIO BCM | Description |
|-----|----------|-------------|
| Row 0 | GPIO 4 | Row select |
| Row 1 | GPIO 17 | Row select |
| Row 2 | GPIO 27 | Row select |
| Row 3 | GPIO 22 | Row select |
| Row 4 | GPIO 5 | Row select |
| Row 5 | GPIO 6 | Row select |
| Row 6 | GPIO 13 | Row select |
| Row 7 | GPIO 19 | Row select |

**Column Pins (Cathode, -)**
| Column | GPIO BCM | Description |
|--------|----------|-------------|
| Col 0 | GPIO 26 | Column data |
| Col 1 | GPIO 12 | Column data |
| Col 2 | GPIO 16 | Column data |
| Col 3 | GPIO 20 | Column data |
| Col 4 | GPIO 21 | Column data |
| Col 5 | GPIO 7 | Column data |
| Col 6 | GPIO 8 | Column data |
| Col 7 | GPIO 25 | Column data |

### Disabled Components

- **LED RGB**: Removed to free GPIO pins (visual effects shown on web)
- **FND 7-Segment**: Removed to free GPIO pins (score shown on web)

## Team

- Team Leader: 김태형 (Development)
- Team Member: 김지환 (Presentation)
- Team Member: 나민서 (Planning)
- Supervisor: 송기범 교수님
