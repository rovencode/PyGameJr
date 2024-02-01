from pygamejr import game

game.start()

# Create some shapes
rect = game.create_rect(60, 60, bottom_left=(100, 100), color="blue")
ellipse = game.create_ellipse(80, 80, bottom_left=(200, 200), color="yellow")
triangle = game.create_polygon(sides=3, width=60, height=60,
                               bottom_left=(300, 300), color="green")

# Move triangle using keyboard
def triangle_keyboard(triangle, keys):
    if "left" in keys:
        triangle.move_by((-2, 0))
    elif "right" in keys:
        triangle.move_by((2, 0))
    elif "up" in keys:
        triangle.move_by((0, 2))
    elif "down" in keys:
        triangle.move_by((0, -2))

    if triangle.touches([rect, ellipse]):
        triangle.color = "red"
    else:
        triangle.color = "green"

game.handle(triangle.on_keypress, triangle_keyboard)

game.keep_running()
