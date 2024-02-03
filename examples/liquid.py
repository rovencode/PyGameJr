import random
from pygamejr import game, DrawOptions

game.start(gravity=-900,
           screen_width=600, screen_height=600, screen_color=(0,0,0))

game.create_screen_walls(left=True, right=True, bottom=True)

ball = game.create_circle(center=(300, 800), radius=100, color="red",
                          mass=100)

particles = []
for _ in range(1000):
    particle = game.create_circle(center=(random.randint(100, 450),
                                          random.randint(480, 580)),
                                  radius=3, color="blue",
                                  mass=1)
    particles.append(particle)

game.keep_running()