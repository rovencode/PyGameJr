from pygamejr import game

game.start()

# Create some shapes
rect = game.create_rect(60, 60, 100, 100, "blue")
ellipse = game.create_ellipse(80, 80, 200, 200, "yellow")
triangle = game.create_polygon(sides=3, width=60, height=60, x=300, y=300, color="green")

# add new costume for triangle
triangle.add_costume_polygon("collision", sides=3, width=60, height=60, color="red")

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
