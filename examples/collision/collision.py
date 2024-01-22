from pygamejr import game

game.start()

# Create some shapes
rect = game.create_rect(60, 60, 100, 100, "blue")
ellipse = game.create_ellipse(80, 80, 500, 500, "yellow")
triangle = game.create_polygon(3, 60, 60, 400, 400, color="green")

# add new costume for triangle
triangle.add_costume_polygon("collision", 3, 60, 60, color="red")

# Move triangle using keyboard
def triangle_keyboard(triangle, keys):
    if "left" in keys:
        triangle.move(-2, 0)
    elif "right" in keys:
        triangle.move(2, 0)
    elif "up" in keys:
        triangle.move(0, -2)
    elif "down" in keys:
        triangle.move(0, 2)

    if triangle.touches([rect, ellipse]):
        triangle.set_costume("collision")
    else:
        triangle.set_costume("")

game.handle(triangle.on_keypress, triangle_keyboard)

game.keep_running()
