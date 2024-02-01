from pygamejr import game

game.start(gravity=0)

ground = 200
game.create_screen_walls(left=True, right=True, top=True, bottom=ground,
                         friction=0.3)

# create bricks
for x in range(5):
    for y in range(10):
        game.create_rect(center=(500 + x*50,  ground + y*20),
                         width=20, height=20,
                         color=game.random_color(),
                         density=0.0, friction=0.3)

def on_key_press(keys):
    if " " in keys:
        bullet = game.create_circle(center=(0, ground+165), radius=15, color="red",
                           density=100.0, friction=0.3)
        bullet.apply_impulse((200000, 0))


game.keep_running()