"""Flappy Bird Game Implementation"""
import random
import time
from threading import Thread, Lock


class FlappyBirdGame:
    """Flappy Bird Game Logic"""

    def __init__(self, width=16, height=16, difficulty='Normal'):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.speed = self.get_speed_by_difficulty()

        self.bird_y = height // 2
        self.bird_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -2.5

        self.pipes = []
        self.pipe_gap = 4
        self.pipe_frequency = 40  # frames between pipes
        self.frame_count = 0

        self.score = 0
        self.game_over = False
        self.running = False
        self.lock = Lock()

    def get_speed_by_difficulty(self):
        """Get game speed based on difficulty"""
        speeds = {
            'Easy': 0.1,
            'Normal': 0.07,
            'Hard': 0.05
        }
        return speeds.get(self.difficulty, 0.07)

    def jump(self):
        """Make bird jump"""
        with self.lock:
            if not self.game_over:
                self.bird_velocity = self.jump_strength

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        with self.lock:
            # Update bird position
            self.bird_velocity += self.gravity
            self.bird_y += self.bird_velocity

            # Check ground/ceiling collision
            if self.bird_y < 0 or self.bird_y >= self.height:
                self.game_over = True
                return

            # Spawn pipes
            self.frame_count += 1
            if self.frame_count >= self.pipe_frequency:
                self.frame_count = 0
                pipe_gap_y = random.randint(2, self.height - self.pipe_gap - 2)
                self.pipes.append({
                    'x': self.width,
                    'gap_y': pipe_gap_y,
                    'scored': False
                })

            # Update pipes
            for pipe in self.pipes[:]:
                pipe['x'] -= 1

                # Remove off-screen pipes
                if pipe['x'] < -2:
                    self.pipes.remove(pipe)

                # Check collision
                bird_x = 2
                if pipe['x'] <= bird_x <= pipe['x'] + 1:
                    if (int(self.bird_y) < pipe['gap_y'] or
                            int(self.bird_y) > pipe['gap_y'] + self.pipe_gap):
                        self.game_over = True
                        return

                # Score when passing pipe
                if not pipe['scored'] and pipe['x'] < bird_x:
                    pipe['scored'] = True
                    self.score += 1

    def get_state(self):
        """Get current game state"""
        with self.lock:
            return {
                'bird_y': int(self.bird_y),
                'pipes': self.pipes.copy(),
                'score': self.score,
                'game_over': self.game_over,
                'width': self.width,
                'height': self.height,
                'pipe_gap': self.pipe_gap
            }

    def reset(self):
        """Reset game"""
        with self.lock:
            self.bird_y = self.height // 2
            self.bird_velocity = 0
            self.pipes = []
            self.frame_count = 0
            self.score = 0
            self.game_over = False

    def run_game_loop(self, hardware=None):
        """Run game loop"""
        self.running = True

        while self.running:
            if not self.game_over:
                self.update()

                if hardware:
                    hardware['fnd'].set_score(self.score)
                    if self.game_over:
                        hardware['buzzer'].game_over_sound()
                        hardware['led'].game_over_effect()

            time.sleep(self.speed)

    def stop(self):
        """Stop game loop"""
        self.running = False
