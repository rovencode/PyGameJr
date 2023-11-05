from pygamejr import game

game.start()

ball = game.create_sprite("ball.gif", 100, 100)
x_speed, y_speed = 2, 2

while True:
    ball.move(x_speed, y_speed)

    rect = ball.rect()

    if rect.left < 0 or rect.right > game.width:
        x_speed = -x_speed
    if rect.top < 0 or rect.bottom > game.height:
        y_speed = -y_speed

    game.update()