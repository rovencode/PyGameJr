from pygamejr import game

game.start()

ball = game.create_sprite("ball.gif", 100, 100)

def ball_keyboard(ball, keys):
    if "left" in keys:
        ball.rect = ball.rect.move(-2, 0)
    elif "right" in keys:
        ball.rect = ball.rect.move(2, 0)
    elif "up" in keys:
        ball.rect = ball.rect.move(0, -2)
    elif "down" in keys:
        ball.rect = ball.rect.move(0, 2)

game.handle(ball.on_keypress, ball_keyboard)

while True:
    game.update()