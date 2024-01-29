from pygamejr import game

game.start()

ball = game.create_image("ball.gif", (100, 100))
x_speed, y_speed = 4, 4

while game.is_running():
    ball.move_by((x_speed, y_speed))

    if game.too_left(ball) or game.too_right(ball):
        x_speed = -x_speed
    if game.too_top(ball) or game.too_bottom(ball):
        y_speed = -y_speed

    game.update()