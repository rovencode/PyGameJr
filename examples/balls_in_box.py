import random
from pygamejr import game, Physics, Vector2

game.start(gravity=0.0)

game.create_screen_walls(bottom=True, left=True, right=True, top=True,
                         enable_physcs=True)

for i in range(5):
    ball1 = game.create_image("ball.gif",
                              random.randint(100, game.get_screen_width()-100),
                              random.randint(100, game.get_screen_height()-100),
                              physics=Physics(enabled=True,
                                              velocity=Vector2(random.randint(-200, 200),
                                                                           random.randint(-200, 200)),
                                              mass=random.randint(1, 10)))

game.keep_running()