import random
from pygamejr import game

game.start(gravity=0)

game.create_screen_walls(bottom=True, left=True, right=True, top=True, elasticity=1)

for i in range(30):
    ball1 = game.create_circle(radius=20, image_path="ball.gif",
                              center=(random.randint(100, game.screen_width()-100),
                                      random.randint(100, game.screen_height()-100)),
                              density=1, elasticity=1,
                              velocity=(random.uniform(-200, 200),
                                        random.uniform(-200, 200)),
                              angular_velocity=random.uniform(-50, 50))
    ball1.fit_image()



game.keep_running()