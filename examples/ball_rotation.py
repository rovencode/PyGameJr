from pygamejr import game

game.show_mouse_coordinates = True
game.set_camera_controls(True)
game.start()

ball1 = game.create_circle(radius=100, color="red",
                           image_path="ball.gif",
                           center=(200,200),
                           scale_xy=(1., 1.), border=0)
ball2 = game.create_polygon_any([(-200, 100), (100,400), (400, 100)], color="blue",
                                image_path="ball.gif",
                                bottom_left=(500,100),
                                border=0)
ball3 = game.create_rect(width=100, height=50, color='yellow',
                         image_path="ball.gif",
                         bottom_left=(300,300), scale_xy=(1., 1.), border=0)

while game.is_running():
    #ball1.turn_by(1)
    game.update()