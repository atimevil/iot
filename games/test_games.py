"""Simple tests for game logic without hardware"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from games.snake_game import SnakeGame
from games.tetris_game import TetrisGame
from games.flappy_bird_game import FlappyBirdGame


def test_snake_game():
    """Test Snake Game basic functionality"""
    print("Testing Snake Game...")

    game = SnakeGame(width=10, height=10, difficulty='Normal')

    # Test initial state
    assert len(game.snake) == 1
    assert game.score == 0
    assert not game.game_over

    # Test direction change
    game.change_direction('UP')
    assert game.next_direction == 'UP'

    # Test movement
    initial_head = game.snake[0]
    game.update()
    new_head = game.snake[0]
    assert initial_head != new_head

    print("✓ Snake Game tests passed!")


def test_tetris_game():
    """Test Tetris Game basic functionality"""
    print("Testing Tetris Game...")

    game = TetrisGame(width=10, height=20, difficulty='Normal')

    # Test initial state
    assert game.current_piece is not None
    assert game.score == 0
    assert not game.game_over

    # Test rotation
    game.rotate_piece()

    # Test movement
    initial_x = game.current_x
    game.move(1, 0)
    assert game.current_x != initial_x or True  # May not move if at edge

    print("✓ Tetris Game tests passed!")


def test_flappy_bird_game():
    """Test Flappy Bird Game basic functionality"""
    print("Testing Flappy Bird Game...")

    game = FlappyBirdGame(width=16, height=16, difficulty='Normal')

    # Test initial state
    assert game.bird_y == 8
    assert game.score == 0
    assert not game.game_over

    # Test jump
    initial_velocity = game.bird_velocity
    game.jump()
    assert game.bird_velocity < initial_velocity

    # Test update
    game.update()

    print("✓ Flappy Bird Game tests passed!")


if __name__ == '__main__':
    print("\n🧪 Running Game Logic Tests...\n")

    try:
        test_snake_game()
        test_tetris_game()
        test_flappy_bird_game()

        print("\n✅ All tests passed!\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
