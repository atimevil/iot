"""Tetris Game Implementation"""
import random
import time
from threading import Thread, Lock


class TetrisGame:
    """Tetris Game Logic"""

    # Tetromino shapes
    SHAPES = {
        'I': [[1, 1, 1, 1]],
        'O': [[1, 1], [1, 1]],
        'T': [[0, 1, 0], [1, 1, 1]],
        'S': [[0, 1, 1], [1, 1, 0]],
        'Z': [[1, 1, 0], [0, 1, 1]],
        'J': [[1, 0, 0], [1, 1, 1]],
        'L': [[0, 0, 1], [1, 1, 1]]
    }

    def __init__(self, width=8, height=16, difficulty='Normal'):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.speed = self.get_speed_by_difficulty()

        self.board = [[0] * width for _ in range(height)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.running = False
        self.lock = Lock()

        self.spawn_piece()

    def get_speed_by_difficulty(self):
        """Get game speed based on difficulty"""
        speeds = {
            'Easy': 0.8,
            'Normal': 0.5,
            'Hard': 0.3
        }
        return speeds.get(self.difficulty, 0.5)

    def spawn_piece(self):
        """Spawn new tetromino"""
        shape_name = random.choice(list(self.SHAPES.keys()))
        self.current_piece = self.SHAPES[shape_name]
        self.current_x = self.width // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0

        # Check if spawn position is valid
        if self.check_collision(self.current_piece, self.current_x, self.current_y):
            self.game_over = True

    def rotate_piece(self):
        """Rotate current piece 90 degrees clockwise"""
        with self.lock:
            if not self.current_piece:
                return

            # Transpose and reverse rows
            rotated = list(zip(*self.current_piece[::-1]))
            rotated = [list(row) for row in rotated]

            # Check if rotation is valid
            if not self.check_collision(rotated, self.current_x, self.current_y):
                self.current_piece = rotated

    def move(self, dx, dy):
        """Move piece by dx, dy"""
        with self.lock:
            new_x = self.current_x + dx
            new_y = self.current_y + dy

            if not self.check_collision(self.current_piece, new_x, new_y):
                self.current_x = new_x
                self.current_y = new_y
                return True
            return False

    def check_collision(self, piece, x, y):
        """Check if piece collides with board or boundaries"""
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx

                    # Check boundaries
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return True

                    # Check board collision (ignore if above board)
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True

        return False

    def lock_piece(self):
        """Lock current piece to board"""
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    y = self.current_y + row_idx
                    x = self.current_x + col_idx
                    if 0 <= y < self.height:
                        self.board[y][x] = 1

        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """Clear completed lines"""
        new_lines_cleared = 0
        y = self.height - 1

        while y >= 0:
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0] * self.width)
                new_lines_cleared += 1
            else:
                y -= 1

        self.lines_cleared += new_lines_cleared
        self.score += new_lines_cleared * 10

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        # Try to move piece down
        if not self.move(0, 1):
            # Piece can't move down, lock it
            self.lock_piece()

    def get_state(self):
        """Get current game state"""
        with self.lock:
            return {
                'board': [row[:] for row in self.board],  # Send board without current piece
                'current_piece': self.current_piece,
                'current_x': self.current_x,
                'current_y': self.current_y,
                'score': self.score,
                'lines_cleared': self.lines_cleared,
                'game_over': self.game_over,
                'width': self.width,
                'height': self.height
            }

    def reset(self):
        """Reset game"""
        with self.lock:
            self.board = [[0] * self.width for _ in range(self.height)]
            self.score = 0
            self.lines_cleared = 0
            self.game_over = False
            self.spawn_piece()

    def run_game_loop(self, hardware=None):
        """Run game loop"""
        self.running = True

        while self.running:
            if not self.game_over:
                self.update()

                # Update hardware if available (buzzer only for now)
                if hardware and hasattr(hardware, 'beep'):
                    try:
                        if self.game_over:
                            hardware.beep(0.2)  # Game over sound
                    except:
                        pass  # Ignore hardware errors

            time.sleep(self.speed)

    def stop(self):
        """Stop game loop"""
        self.running = False
