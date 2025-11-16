"""Flask Web Application for Game Console"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import os
from threading import Thread

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.snake_game import SnakeGame
from games.tetris_game import TetrisGame
from games.flappy_bird_game import FlappyBirdGame

# Try to import hardware drivers
try:
    from drivers.lcd_driver import LCD
    from drivers.buzzer_driver import Buzzer
    from drivers.led_driver import LED
    from drivers.fnd_driver import FND
    from drivers.dotmatrix_driver import DotMatrix
    HARDWARE_AVAILABLE = True
except Exception as e:
    print(f"Hardware drivers not available: {e}")
    HARDWARE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspberry_pi_game_console'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global game instances
current_game = None
game_thread = None
hardware = None

# Initialize hardware if available
if HARDWARE_AVAILABLE:
    try:
        hardware = {
            'lcd': LCD(),
            'buzzer': Buzzer(),
            'led': LED(),
            'fnd': FND(),
            'dotmatrix': DotMatrix()
        }
        hardware['lcd'].display_two_lines("Game Console", "Ready!")
    except Exception as e:
        print(f"Could not initialize hardware: {e}")
        hardware = None


def game_state_broadcaster():
    """Broadcast game state to all connected clients"""
    global current_game

    while current_game and current_game.running:
        if current_game:
            state = current_game.get_state()
            socketio.emit('game_state', state)
            socketio.sleep(0.05)  # 20 FPS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/game/<game_name>')
def game_page(game_name):
    """Game page"""
    if game_name not in ['snake', 'tetris', 'flappy']:
        return "Game not found", 404
    return render_template(f'{game_name}.html')


@socketio.on('start_game')
def handle_start_game(data):
    """Start a new game"""
    global current_game, game_thread

    game_name = data.get('game')
    difficulty = data.get('difficulty', 'Normal')

    # Stop current game if running
    if current_game:
        current_game.stop()
        if game_thread:
            game_thread.join()

    # Create new game
    if game_name == 'snake':
        current_game = SnakeGame(difficulty=difficulty)
        if hardware:
            hardware['lcd'].display_two_lines("Snake Game", f"Difficulty: {difficulty}")
    elif game_name == 'tetris':
        current_game = TetrisGame(difficulty=difficulty)
        if hardware:
            hardware['lcd'].display_two_lines("Tetris Game", f"Difficulty: {difficulty}")
    elif game_name == 'flappy':
        current_game = FlappyBirdGame(difficulty=difficulty)
        if hardware:
            hardware['lcd'].display_two_lines("Flappy Bird", f"Difficulty: {difficulty}")
    else:
        emit('error', {'message': 'Unknown game'})
        return

    # Start game loop in separate thread
    game_thread = Thread(target=current_game.run_game_loop, args=(hardware,))
    game_thread.start()

    # Start state broadcaster
    socketio.start_background_task(game_state_broadcaster)

    # Start LED effect
    if hardware:
        hardware['led'].game_start_effect()

    emit('game_started', {'game': game_name, 'difficulty': difficulty})


@socketio.on('game_input')
def handle_game_input(data):
    """Handle game input from client"""
    global current_game

    if not current_game:
        return

    action = data.get('action')
    game_type = data.get('game')

    if game_type == 'snake':
        if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            current_game.change_direction(action)

    elif game_type == 'tetris':
        if action == 'LEFT':
            current_game.move(-1, 0)
        elif action == 'RIGHT':
            current_game.move(1, 0)
        elif action == 'DOWN':
            current_game.move(0, 1)
        elif action == 'ROTATE':
            current_game.rotate_piece()

    elif game_type == 'flappy':
        if action == 'JUMP':
            current_game.jump()


@socketio.on('reset_game')
def handle_reset_game():
    """Reset current game"""
    global current_game

    if current_game:
        current_game.reset()
        if hardware:
            hardware['fnd'].reset_score()
            hardware['led'].all_off()
        emit('game_reset')


@socketio.on('stop_game')
def handle_stop_game():
    """Stop current game"""
    global current_game, game_thread

    if current_game:
        current_game.stop()
        if game_thread:
            game_thread.join()
        current_game = None

        if hardware:
            hardware['lcd'].display_two_lines("Game Stopped", "Select New Game")
            hardware['fnd'].reset_score()
            hardware['led'].all_off()

        emit('game_stopped')


@app.route('/api/games')
def get_games():
    """Get list of available games"""
    games = [
        {
            'id': 'snake',
            'name': 'Snake Game',
            'description': 'Classic snake game - eat food and grow longer!'
        },
        {
            'id': 'tetris',
            'name': 'Tetris',
            'description': 'Arrange falling blocks to clear lines!'
        },
        {
            'id': 'flappy',
            'name': 'Flappy Bird',
            'description': 'Navigate through pipes by jumping!'
        }
    ]
    return jsonify(games)


@app.route('/api/difficulties')
def get_difficulties():
    """Get available difficulty levels"""
    return jsonify(['Easy', 'Normal', 'Hard'])


if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    finally:
        # Cleanup hardware on exit
        if hardware:
            for device in hardware.values():
                if hasattr(device, 'cleanup'):
                    device.cleanup()
