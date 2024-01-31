import random
from pygamejr import game, Physics, Vector2

game.start(gravity=0)

game.create_screen_walls(bottom=True, left=True, right=True, top=True)

for i in range(50):
    ball1 = game.create_circle(radius=20, image_path="ball.gif",
                              center=(random.randint(100, game.screen_width()-100),
                                      random.randint(100, game.screen_height()-100)),
                              density=1,
                              velocity=(random.uniform(-200, 200),
                                        random.uniform(-200, 200)),
                              angular_velocity=random.uniform(-5, 5))



game.keep_running()