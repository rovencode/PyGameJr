from pygamejr import game

game.start()

# Create a rectangle
rect = game.create_rect(20, 20, 100, 100, "blue")
ellipse = game.create_ellipse(20, 20, 50, 50, "red")
triangle = game.create_polygon(3, 20, 20, 80, 80, color="black")
line = game.create_line(250, 100, 300, 300, "green", border=5)

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
        triangle.set_color("yellow")
    else:
        triangle.set_color("black")

game.handle(triangle.on_keypress, triangle_keyboard)

while game.is_running():

    game.update()