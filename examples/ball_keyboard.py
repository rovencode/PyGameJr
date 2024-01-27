from pygamejr import game

game.start()

ball = game.create_image("ball.gif", 100, 100)
speed = 4
def ball_keyboard(ball, keys):
    if "left" in keys:
        ball.move_by(-speed, 0)
    elif "right" in keys:
        ball.move_by(speed, 0)
    elif "up" in keys:
        ball.move_by(0, -speed)
    elif "down" in keys:
        ball.move_by(0, speed)

game.handle(ball.on_keypress, ball_keyboard)

game.keep_running()