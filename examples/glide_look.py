from pygamejr import game

game.start()

triangle = game.create_polygon_any([(50,50), (20, 150), (80, 150)], color="green")

while game.is_running():
    triangle.turn_towards(game.mouse_xy())
    triangle.glide_to(game.mouse_xy(), speed=2)

    if triangle.touches_at(game.mouse_xy()):
        triangle.add_text("BOOM!!")
    else:
        triangle.remove_text("BOOM!!")

    game.update()
