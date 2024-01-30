import random
from pygamejr import game, Physics, Vector2

game.start()

ball = game.create_circle(radius=200, image_path="ball.gif", center=(500,500))

while game.is_running():
    ball.turn_by(1)
    game.update()