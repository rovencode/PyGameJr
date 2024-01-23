from pygamejr import game

game.start(ground_y=1.0, gravity=0.1)

ball1 = game.create_image("ball.gif", 100, 100, enable_physics=True)
ball2 = game.create_image("ball.gif", 400, 100, enable_physics=False)

game.keep_running()