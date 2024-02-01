from pygamejr import game

game.start()

ball = game.create_image("ball.gif", (100, 100))
speed = 4

# mouse button event
def ball_mouse(ball, buttons):
    if 'left' in buttons:
        ball.move_by((speed, 0))
    elif 'right' in buttons:
        ball.move_by((-speed, 0))
    elif 'middle' in buttons:
        ball.move_by((speed, 0))
game.handle(ball.on_mousebutton, ball_mouse)

# mouse wheel event
def ball_mousewheel(ball, horizotal_scroll, vertical_scroll,
                    *args):
    ball.move_by((horizotal_scroll, vertical_scroll))
game.handle(ball.on_mousewheel, ball_mousewheel)

# mouse move event
def screen_mousemove(noone, pos, *args):
    game.add_text("Mouse at %s" % (pos,), name="coord")
game.handle(game.noone.on_mousemove, screen_mousemove)

game.keep_running()