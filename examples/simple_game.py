from pygamejr import game

game.start(screen_color=(200, 200, 200))

x, y = 100, 100
e = game.create_ellipse(100, 60, x, y, color=(50, 100, 10))
e.add_costume_ellipse('roven', 100, 60, color="yellow")

hex = game.create_polygon(sides=6, width=200, height=200, x=300, y=300, color="lime")

def ayani_keyboard(obj, keys):
    if "left" in keys:
        obj.move_by(-4, 0)
    elif "right" in keys:
        obj.move_by(4, 0)
    elif "up" in keys:
        obj.move_by(0, -4)
    elif "down" in keys:
        obj.move_by(0, 4)
game.handle(hex.on_keypress, ayani_keyboard)


while game.is_running():
    if e.y() >= game.screen_height()-e.height():
        e.move_to(e.x(), game.screen_height()-e.height())
    else:
        e.move_by(0, 1)

    if e.touches(hex):
        e.set_costume('roven')
    else:
        e.set_costume('')

    game.update()



