from pygamejr import game

game.start()

# Create a rectangle
rect = game.create_rect(20, 20, 100, 100, "blue")
ellipse = game.create_ellipse(20, 20, 50, 50, "red")
triangle = game.create_polygon(3, 20, 20, 80, 80)
line = game.create_line(250, 100, 300, 300, "green", border=5)

while game.is_running():
    game.update()