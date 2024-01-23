from pygamejr import game, Physics

game.start(ground_y=1.0, gravity=0.1)

ball1 = game.create_image("ball.gif", 100, 100, physics=Physics(enabled=True))
ball2 = game.create_image("ball.gif", 400, 100)

game.keep_running()