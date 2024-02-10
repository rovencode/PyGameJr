from pygamejr import game

game.start()

cat = game.create_image("cat.sprite3", center=(300, 300))
cat.start_animation()

while game.is_running():
    cat.turn_towards(game.mouse_xy())
    cat.glide_to(game.mouse_xy(), speed=2)

    if cat.touches_at(game.mouse_xy()):
        cat.add_text("BOOM!!")
    else:
        cat.remove_text("BOOM!!")

    game.update()
