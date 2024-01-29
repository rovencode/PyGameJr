from pygamejr import game, Physics

game.start(gravity=-100)

game.create_screen_walls(bottom=True)

ball1 = game.create_image("ball.gif", (100, 100), density=1)
ball2 = game.create_image("ball.gif", (400, 100))

game.keep_running()