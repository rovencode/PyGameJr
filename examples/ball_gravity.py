from pygamejr import game, Physics

game.start(gravity=400)

game.create_screen_walls(bottom=True, enable_physcs=True)

ball1 = game.create_image("ball.gif", 100, 100, physics=Physics(enabled=True))
ball2 = game.create_image("ball.gif", 400, 100)

game.keep_running()