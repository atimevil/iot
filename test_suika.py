from games.suika_game import SuikaGame
import time

g = SuikaGame()
print('Initial game_over:', g.game_over)

g.drop_fruit()
print('After drop game_over:', g.game_over)

for i in range(30):
    g.update()
    time.sleep(0.016)

    if i % 5 == 0:
        if g.fruits:
            fruit = g.fruits[0]
            pos_y = fruit['body'].position.y
            vel = fruit['body'].velocity.length
            print(f'Update {i+1}: y={pos_y:.1f}, vel={vel:.1f}, game_over={g.game_over}')
        else:
            print(f'Update {i+1}: No fruits, game_over={g.game_over}')

    if g.game_over:
        print('GAME OVER!')
        break

print(f'Final: game_over={g.game_over}, fruits={len(g.fruits)}')
