"""Flask Web Application for Game Console - IR Remote Only Version"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import os
from threading import Thread

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.snake_game import SnakeGame
from games.tetris_game import TetrisGame
from games.suika_game import SuikaGame
from database.models import db

# Try to import hardware drivers (IR and Buzzer only)
try:
    from drivers.ir_driver import IRRemote
    from drivers.buzzer_driver import Buzzer
    HARDWARE_AVAILABLE = True
except Exception as e:
    print(f"Hardware drivers not available: {e}")
    HARDWARE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'raspberry_pi_game_console_v2'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global game instances
current_game = None
game_thread = None
buzzer = None
ir_remote = None

# Initialize hardware if available
if HARDWARE_AVAILABLE:
    try:
        buzzer = Buzzer()
        ir_remote = IRRemote()
        print("[OK] Hardware initialized: Buzzer + IR Remote")
    except Exception as e:
        print(f"Could not initialize hardware: {e}")
        buzzer = None
        ir_remote = None


def handle_ir_button(button_name):
    """Handle IR remote button press and send to game via WebSocket"""
    global current_game

    if not current_game:
        return

    print(f"[IR] Button pressed: {button_name}")

    # Determine game type
    game_type = None
    if isinstance(current_game, SnakeGame):
        game_type = 'snake'
    elif isinstance(current_game, TetrisGame):
        game_type = 'tetris'
    elif isinstance(current_game, SuikaGame):
        game_type = 'suika'

    if not game_type:
        return

    # Map button to action based on game
    action = None

    if game_type == 'snake':
        # Snake uses directional buttons
        if button_name in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            action = button_name

    elif game_type == 'tetris':
        # Tetris: UP=rotate, DOWN=drop, LEFT/RIGHT=move
        if button_name == 'UP':
            action = 'ROTATE'
        elif button_name in ['DOWN', 'LEFT', 'RIGHT']:
            action = button_name

    elif game_type == 'suika':
        # Suika: LEFT/RIGHT=move, SELECT/DOWN=drop
        if button_name in ['LEFT', 'RIGHT']:
            action = button_name
        elif button_name in ['SELECT', 'DOWN']:
            action = 'SELECT'

    # Send action to game
    if action:
        if game_type == 'snake':
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
        elif game_type == 'suika':
            if action == 'LEFT':
                current_game.move_drop_position('LEFT')
            elif action == 'RIGHT':
                current_game.move_drop_position('RIGHT')
            elif action == 'SELECT':
                current_game.drop_fruit()


# Start IR remote reading if available
if ir_remote:
    try:
        ir_remote.start_reading(handle_ir_button)
        print("[IR] IR remote listening started")
    except Exception as e:
        print(f"[IR] Could not start IR remote: {e}")


def game_state_broadcaster():
    """Broadcast game state to all connected clients"""
    global current_game

    while current_game and current_game.running:
        if current_game:
            state = current_game.get_state()
            socketio.emit('game_state', state)
            socketio.sleep(0.05)  # 20 FPS


# ===== ROUTES =====

@app.route('/')
def index():
    """Main menu page"""
    return render_template('index.html')


@app.route('/game/<game_name>')
def game_page(game_name):
    """Game page"""
    valid_games = ['snake', 'tetris', 'suika']
    if game_name not in valid_games:
        return "Game not found", 404
    return render_template(f'{game_name}.html')


@app.route('/scoreboard')
def scoreboard():
    """Scoreboard page"""
    return render_template('scoreboard.html')


@app.route('/api/games')
def get_games():
    """Get list of available games"""
    games = [
        {
            'id': 'snake',
            'name': 'Snake',
            'description': 'Classic snake game on 8x8 grid',
            'grid': '8x8',
            'difficulty': True
        },
        {
            'id': 'tetris',
            'name': 'Tetris',
            'description': 'Block puzzle on 8x16 grid',
            'grid': '8x16',
            'difficulty': False
        },
        {
            'id': 'suika',
            'name': 'Suika (수박게임)',
            'description': 'Merge fruits to create watermelon',
            'grid': 'Physics',
            'difficulty': False
        }
    ]
    return jsonify(games)


@app.route('/api/scores/<game_name>')
def get_game_scores(game_name):
    """Get top scores for a specific game"""
    difficulty = request.args.get('difficulty')
    limit = int(request.args.get('limit', 10))

    scores = db.get_top_scores(game_name, limit=limit, difficulty=difficulty)
    stats = db.get_game_stats(game_name)

    return jsonify({
        'scores': scores,
        'stats': stats
    })


@app.route('/api/scores/all')
def get_all_scores():
    """Get top scores across all games"""
    limit = int(request.args.get('limit', 20))
    scores = db.get_all_top_scores(limit=limit)
    stats = db.get_all_stats()

    return jsonify({
        'scores': scores,
        'stats': stats
    })


# ===== WEBSOCKET EVENTS =====

@socketio.on('start_game')
def handle_start_game(data):
    """Start a new game"""
    global current_game, game_thread

    game_name = data.get('game')
    difficulty = data.get('difficulty', 'Normal')
    player_name = data.get('player_name', 'Player')

    # Stop current game if running
    if current_game:
        current_game.stop()
        if game_thread and game_thread.is_alive():
            game_thread.join(timeout=3.0)
            if game_thread.is_alive():
                print("Warning: Previous game thread did not stop cleanly")
        current_game = None
        game_thread = None

    # Create new game
    if game_name == 'snake':
        current_game = SnakeGame(difficulty=difficulty)
    elif game_name == 'tetris':
        current_game = TetrisGame(difficulty=difficulty)
    elif game_name == 'suika':
        # Check if pymunk is available for Suika game
        try:
            import pymunk
            current_game = SuikaGame()
        except ImportError:
            emit('error', {'message': 'Suika game requires pymunk library. Please install: pip install pymunk'})
            return
    else:
        emit('error', {'message': 'Unknown game'})
        return

    # Start game loop in separate thread
    game_thread = Thread(target=current_game.run_game_loop, args=(buzzer,))
    game_thread.start()

    # Start state broadcaster
    socketio.start_background_task(game_state_broadcaster)

    emit('game_started', {
        'game': game_name,
        'difficulty': difficulty,
        'player_name': player_name
    })


@socketio.on('game_input')
def handle_game_input(data):
    """Handle game input from client or IR remote"""
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
        elif action == 'ROTATE' or action == 'UP':
            current_game.rotate_piece()

    elif game_type == 'suika':
        if action == 'LEFT':
            current_game.move_drop_position('LEFT')
        elif action == 'RIGHT':
            current_game.move_drop_position('RIGHT')
        elif action == 'SELECT' or action == 'DOWN':
            current_game.drop_fruit()


@socketio.on('reset_game')
def handle_reset_game():
    """Reset current game"""
    global current_game

    if current_game:
        current_game.reset()
        emit('game_reset')


@socketio.on('stop_game')
def handle_stop_game(data):
    """Stop current game and save score"""
    global current_game, game_thread

    if current_game:
        # Save score to database
        game_name = data.get('game')
        player_name = data.get('player_name', 'Player')
        score = current_game.score
        difficulty = getattr(current_game, 'difficulty', None)

        if score > 0:
            db.add_score(game_name, player_name, score, difficulty)

        # Stop game
        current_game.stop()
        if game_thread:
            game_thread.join(timeout=2.0)
        current_game = None

        emit('game_stopped', {'score': score})


@socketio.on('save_score')
def handle_save_score(data):
    """Manually save score"""
    game_name = data.get('game')
    player_name = data.get('player_name', 'Player')
    score = data.get('score', 0)
    difficulty = data.get('difficulty')

    if score > 0:
        db.add_score(game_name, player_name, score, difficulty)
        emit('score_saved', {'success': True})
    else:
        emit('score_saved', {'success': False, 'message': 'Invalid score'})


if __name__ == '__main__':
    try:
        print("=" * 50)
        print("Game Console Server Starting...")
        print("=" * 50)
        print(f"Hardware: {'Available' if HARDWARE_AVAILABLE else 'Simulated'}")
        print(f"Database: SQLite")
        print(f"Games: Snake (8x8), Tetris (8x16), Suika")
        print("=" * 50)
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    finally:
        # Cleanup hardware on exit
        if buzzer:
            buzzer.cleanup()
        if ir_remote:
            ir_remote.cleanup()
