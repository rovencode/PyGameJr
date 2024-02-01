import random
from pygamejr import game, ImagePaintMode, Vec2d

game.show_mouse_coordinates = True
game.set_camera_controls(True)
game.start(screen_title="Mario Animation", screen_image_path="background.jpg",
           gravity=-500)

# create ground
game.create_screen_walls(bottom=112, friction=0.5)

# create Mario
mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,200), scale_xy=(0.5, 0.5),
                          density=1, elasticity=0.6, friction=0.1)
mario.start_animation(frame_time_s=0.2)

# create platforms
platforms = []
pos = Vec2d(300, 250)
for i in range(500):
    platform = game.create_rect(100, 20, image_path="bricks.png",
                    bottom_left=pos,
                    paint_mode=ImagePaintMode.TILE, scale_xy=(0.5, 0.5),
                    density=1, friction=0.5, fixed_object=True)
    platforms.append(platform)
    pos += Vec2d(random.randint(0, 100), random.randint(-100, 100))

# play background music
game.play_sound('music.mp3', loops=-1)

def mario_keyboard(mario, keys):
    if "left" in keys:
        mario.apply_impulse((-10000, 0))
    elif "right" in keys:
        mario.apply_impulse((10000, 0))
    elif "up" in keys:
        mario.apply_impulse((0, 50000))
        game.play_sound('jump.mp3')
    elif "down" in keys:
        mario.apply_impulse((0, -1000))
game.handle(mario.on_keypress, mario_keyboard)

game.keep_running()