from pygamejr import game

game.start()

ball = game.create_sprite("ball.gif", 100, 100)
x_speed, y_speed = 2, 2

while True:
    ball.rect = ball.rect.move(x_speed, y_speed)

    if ball.rect.left < 0 or ball.rect.right > game.width:
        x_speed = -x_speed
    if ball.rect.top < 0 or ball.rect.bottom > game.height:
        y_speed = -y_speed

    game.rest()