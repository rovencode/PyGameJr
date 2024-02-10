from pygamejr import game

game.start("game", screen_color = "grey", screen_width=1024, screen_height=768)

circle = game.create_ellipse(100, 100, 100, 100, color = "green")

rectangle = game.create_rect(50, 100, 400, 200, color = "yellow")
rectangle2 = game.create_rect(50, 100, 750, 200, color = "yellow")

dir = 1

while game.is_running():

    if rectangle.y() >= game.screen_height()-rectangle.height():
        dir = -1
    elif rectangle.y() <= 0:
        dir = 1
        
    if rectangle2.y() >= game.screen_height()-rectangle.height():
        dir = -1
    elif rectangle2.y() <= 0:
        dir = 1

    rectangle2.move_by(0, dir*4)

    game.update()

