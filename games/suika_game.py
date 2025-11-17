"""Suika Game (Watermelon Game) - Physics-based fruit merging puzzle"""
import random
import time
import threading

try:
    import pymunk
    PYMUNK_AVAILABLE = True
except ImportError:
    PYMUNK_AVAILABLE = False
    print("Warning: pymunk not available. Suika game will use simplified physics.")


class SuikaGame:
    """Suika (Watermelon) Game - Merge fruits to create bigger fruits"""

    # Fruit types (smallest to largest)
    FRUITS = [
        {'name': 'cherry', 'size': 15, 'color': '#FF0000', 'points': 1},
        {'name': 'strawberry', 'size': 20, 'color': '#FF69B4', 'points': 3},
        {'name': 'grape', 'size': 25, 'color': '#9370DB', 'points': 6},
        {'name': 'orange', 'size': 30, 'color': '#FFA500', 'points': 10},
        {'name': 'apple', 'size': 35, 'color': '#FF4500', 'points': 15},
        {'name': 'pear', 'size': 40, 'color': '#90EE90', 'points': 21},
        {'name': 'peach', 'size': 45, 'color': '#FFDAB9', 'points': 28},
        {'name': 'pineapple', 'size': 50, 'color': '#FFD700', 'points': 36},
        {'name': 'melon', 'size': 55, 'color': '#32CD32', 'points': 45},
        {'name': 'watermelon', 'size': 60, 'color': '#00FF00', 'points': 100}
    ]

    def __init__(self, width=400, height=600):
        self.width = width
        self.height = height
        self.score = 0
        self.game_over = False
        self.running = False
        self.lock = threading.Lock()

        # Physics setup
        if PYMUNK_AVAILABLE:
            self.space = pymunk.Space()
            self.space.gravity = (0, 900)  # Gravity
            self._setup_boundaries()
        else:
            self.space = None

        # Game state
        self.fruits = []  # List of fruit objects
        self.next_fruit_type = random.randint(0, 4)  # Next fruit to drop (smaller fruits only)
        self.drop_x = width // 2  # Current drop position

    def _setup_boundaries(self):
        """Setup container boundaries"""
        if not self.space:
            return

        # Bottom
        bottom = pymunk.Segment(self.space.static_body,
                                (0, self.height),
                                (self.width, self.height), 5)
        bottom.friction = 0.5

        # Left wall
        left = pymunk.Segment(self.space.static_body,
                              (0, 0),
                              (0, self.height), 5)
        left.friction = 0.5

        # Right wall
        right = pymunk.Segment(self.space.static_body,
                               (self.width, 0),
                               (self.width, self.height), 5)
        right.friction = 0.5

        self.space.add(bottom, left, right)

    def move_drop_position(self, direction):
        """Move the drop position left or right"""
        with self.lock:
            if direction == 'LEFT':
                self.drop_x = max(40, self.drop_x - 20)
            elif direction == 'RIGHT':
                self.drop_x = min(self.width - 40, self.drop_x + 20)

    def drop_fruit(self):
        """Drop the current fruit"""
        if self.game_over or not PYMUNK_AVAILABLE:
            return

        with self.lock:
            fruit_type = self.next_fruit_type
            fruit_data = self.FRUITS[fruit_type]

            # Create fruit physics body
            mass = fruit_data['size']
            radius = fruit_data['size']
            moment = pymunk.moment_for_circle(mass, 0, radius)

            body = pymunk.Body(mass, moment)
            body.position = (self.drop_x, 50)

            shape = pymunk.Circle(body, radius)
            shape.friction = 0.5
            shape.elasticity = 0.3
            shape.fruit_type = fruit_type

            self.space.add(body, shape)

            fruit_obj = {
                'body': body,
                'shape': shape,
                'type': fruit_type,
                'merged': False,
                'frames_alive': 0  # Track how long fruit has existed
            }

            self.fruits.append(fruit_obj)

            # Generate next fruit
            self.next_fruit_type = random.randint(0, 4)

    def check_merges(self):
        """Check for fruit collisions and merge same types"""
        if not PYMUNK_AVAILABLE:
            return

        with self.lock:
            merged_pairs = []

            # Check all fruit pairs for collisions
            for i, fruit1 in enumerate(self.fruits):
                if fruit1['merged']:
                    continue

                for fruit2 in self.fruits[i + 1:]:
                    if fruit2['merged']:
                        continue

                    # Same fruit type and touching?
                    if fruit1['type'] == fruit2['type']:
                        dist = fruit1['body'].position.get_distance(fruit2['body'].position)
                        combined_radius = self.FRUITS[fruit1['type']]['size'] * 2

                        if dist < combined_radius:
                            merged_pairs.append((fruit1, fruit2))

            # Process merges
            for fruit1, fruit2 in merged_pairs:
                self._merge_fruits(fruit1, fruit2)

    def _merge_fruits(self, fruit1, fruit2):
        """Merge two fruits into a bigger one"""
        # Skip if either fruit is already merged (prevents double-removal errors)
        if fruit1['merged'] or fruit2['merged']:
            return

        if fruit1['type'] >= len(self.FRUITS) - 1:
            # Max fruit reached (watermelon)
            self.score += self.FRUITS[fruit1['type']]['points'] * 2
            # Mark for removal
            fruit1['merged'] = True
            fruit2['merged'] = True
            # Remove from physics space
            try:
                self.space.remove(fruit1['body'], fruit1['shape'])
            except:
                pass  # Already removed
            try:
                self.space.remove(fruit2['body'], fruit2['shape'])
            except:
                pass  # Already removed
            return

        # Mark for removal
        fruit1['merged'] = True
        fruit2['merged'] = True

        # IMPORTANT: Remove old fruits from physics space
        try:
            self.space.remove(fruit1['body'], fruit1['shape'])
        except:
            pass  # Already removed
        try:
            self.space.remove(fruit2['body'], fruit2['shape'])
        except:
            pass  # Already removed

        # Calculate merge position (midpoint)
        merge_x = (fruit1['body'].position.x + fruit2['body'].position.x) / 2
        merge_y = (fruit1['body'].position.y + fruit2['body'].position.y) / 2

        # Create new bigger fruit
        new_type = fruit1['type'] + 1
        fruit_data = self.FRUITS[new_type]

        mass = fruit_data['size']
        radius = fruit_data['size']
        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = (merge_x, merge_y)

        shape = pymunk.Circle(body, radius)
        shape.friction = 0.5
        shape.elasticity = 0.3
        shape.fruit_type = new_type

        self.space.add(body, shape)

        new_fruit = {
            'body': body,
            'shape': shape,
            'type': new_type,
            'merged': False,
            'frames_alive': 0  # Track how long fruit has existed
        }

        self.fruits.append(new_fruit)

        # Add score
        self.score += fruit_data['points']

    def check_game_over(self):
        """Check if any fruit is above the line and stopped"""
        with self.lock:
            for fruit in self.fruits:
                if not fruit['merged']:
                    # Skip newly dropped fruits (wait at least 10 frames = 0.16 seconds)
                    if fruit['frames_alive'] < 10:
                        continue

                    # Check if fruit is above danger line (y < 100)
                    # AND velocity is very low (basically stopped)
                    pos_y = fruit['body'].position.y
                    velocity = fruit['body'].velocity.length

                    # Game over only if fruit is stuck at top (not just passing through)
                    # Velocity < 10 means almost stopped
                    if pos_y < 90 and velocity < 10:
                        self.game_over = True
                        return

    def update(self):
        """Update physics simulation"""
        if self.game_over or not PYMUNK_AVAILABLE:
            return

        # Step physics simulation
        dt = 1.0 / 60.0
        self.space.step(dt)

        # Increment frames_alive for all fruits
        for fruit in self.fruits:
            if not fruit['merged']:
                fruit['frames_alive'] += 1

        # Remove merged fruits
        self.fruits = [f for f in self.fruits if not f['merged']]

        # Check for merges
        self.check_merges()

        # Check game over
        self.check_game_over()

    def get_state(self):
        """Get current game state for rendering"""
        fruits_state = []

        for fruit in self.fruits:
            if not fruit['merged']:
                fruits_state.append({
                    'x': fruit['body'].position.x,
                    'y': fruit['body'].position.y,
                    'type': fruit['type'],
                    'size': self.FRUITS[fruit['type']]['size'],
                    'color': self.FRUITS[fruit['type']]['color'],
                    'name': self.FRUITS[fruit['type']]['name']
                })

        return {
            'fruits': fruits_state,
            'score': self.score,
            'game_over': self.game_over,
            'next_fruit': self.FRUITS[self.next_fruit_type],
            'drop_x': self.drop_x,
            'width': self.width,
            'height': self.height
        }

    def reset(self):
        """Reset game"""
        with self.lock:
            if PYMUNK_AVAILABLE and self.space:
                # Remove all fruits (only if not already merged/removed)
                for fruit in self.fruits:
                    if not fruit['merged']:
                        try:
                            self.space.remove(fruit['body'], fruit['shape'])
                        except:
                            pass  # Already removed, ignore

            self.fruits = []
            self.score = 0
            self.game_over = False
            self.next_fruit_type = random.randint(0, 4)
            self.drop_x = self.width // 2

    def run_game_loop(self, buzzer=None):
        """Run game loop (called in separate thread)"""
        self.running = True

        while self.running:
            if not self.game_over:
                old_score = self.score
                self.update()

                # Play sound on score increase
                if buzzer and self.score > old_score:
                    try:
                        buzzer.score_sound()
                    except:
                        pass

                # Play sound on game over
                if buzzer and self.game_over:
                    try:
                        buzzer.game_over_sound()
                    except:
                        pass

            time.sleep(1.0 / 60.0)  # 60 FPS

    def stop(self):
        """Stop game loop"""
        self.running = False
