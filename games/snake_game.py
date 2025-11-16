"""Snake Game Implementation"""
import random
import time
from threading import Thread, Lock


class SnakeGame:
    """Snake Game Logic"""

    def __init__(self, width=16, height=16, difficulty='Normal'):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.speed = self.get_speed_by_difficulty()

        self.snake = [(width // 2, height // 2)]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.running = False
        self.lock = Lock()

    def get_speed_by_difficulty(self):
        """Get game speed based on difficulty"""
        speeds = {
            'Easy': 0.2,
            'Normal': 0.15,
            'Hard': 0.1
        }
        return speeds.get(self.difficulty, 0.15)

    def generate_food(self):
        """Generate food at random position"""
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food

    def change_direction(self, new_direction):
        """Change snake direction"""
        with self.lock:
            # Prevent 180 degree turns
            opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
            if new_direction != opposite.get(self.direction):
                self.next_direction = new_direction

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        with self.lock:
            self.direction = self.next_direction

            # Calculate new head position
            head_x, head_y = self.snake[0]

            if self.direction == 'UP':
                new_head = (head_x, head_y - 1)
            elif self.direction == 'DOWN':
                new_head = (head_x, head_y + 1)
            elif self.direction == 'LEFT':
                new_head = (head_x - 1, head_y)
            elif self.direction == 'RIGHT':
                new_head = (head_x + 1, head_y)

            # Check wall collision
            if (new_head[0] < 0 or new_head[0] >= self.width or
                    new_head[1] < 0 or new_head[1] >= self.height):
                self.game_over = True
                return

            # Check self collision
            if new_head in self.snake:
                self.game_over = True
                return

            # Add new head
            self.snake.insert(0, new_head)

            # Check food collision
            if new_head == self.food:
                self.score += 1
                self.food = self.generate_food()
            else:
                # Remove tail if no food eaten
                self.snake.pop()

    def get_state(self):
        """Get current game state"""
        with self.lock:
            return {
                'snake': self.snake.copy(),
                'food': self.food,
                'score': self.score,
                'game_over': self.game_over,
                'width': self.width,
                'height': self.height
            }

    def reset(self):
        """Reset game"""
        with self.lock:
            self.snake = [(self.width // 2, self.height // 2)]
            self.direction = 'RIGHT'
            self.next_direction = 'RIGHT'
            self.food = self.generate_food()
            self.score = 0
            self.game_over = False

    def run_game_loop(self, hardware=None):
        """Run game loop in separate thread"""
        self.running = True

        while self.running:
            if not self.game_over:
                self.update()

                # Update hardware if available
                if hardware:
                    hardware['fnd'].set_score(self.score)
                    if self.game_over:
                        hardware['buzzer'].game_over_sound()
                        hardware['led'].game_over_effect()
                    elif self.score > 0:
                        hardware['buzzer'].score_sound()

            time.sleep(self.speed)

    def stop(self):
        """Stop game loop"""
        self.running = False
