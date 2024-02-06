from pygamejr import game

game.start(gravity=-900)

game.create_screen_walls(bottom=True, friction=0.0, elasticity=1)

ball1 = game.create_image("ball.gif", (100, 600), density=10, elasticity=1, friction=0.0)

ball2 = game.create_circle(radius=30, image_path="ball.gif", center=(400, 600),
                           density=1, angular_velocity=5, elasticity=0.8)
ball2.fit_image()

game.keep_running()