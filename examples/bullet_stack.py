from pygamejr import game, DrawOptions

game.start(gravity=-900, screen_fps=250)

ground = 200
# create table
game.create_rect(width=800, height=ground,
                 bottom_left=(100,0), color="blue",
                 fixed_object=True, friction=0.3)

# create back wall
game.create_rect(width=20, height=game.screen_height()//2,
                 bottom_left=(750,ground), color="skyblue",
                 fixed_object=True, friction=0.3)


# create bricks
for x in range(5):
    for y in range(10):
        game.create_rect(bottom_left=(500 + x*50,  ground + y*20),
                         width=20, height=20,
                         color=game.random_color(),
                         mass=10, friction=0.3)

def on_keypress(noone, keys):
    if "space" in keys:
        bullet = game.create_circle(center=(0, ground+165), radius=15, color="red",
                           mass=100, friction=0.3,
                           draw_options=DrawOptions(angle_line_width=1))
        bullet.apply_impulse((200000, 0))
game.handle(game.noone.on_keypress, on_keypress)

game.keep_running()