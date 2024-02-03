import random
import math
from pygamejr import game, ImagePaintMode, Vec2d

game.set_camera_controls(True)
game.start(screen_title="Mario Animation", screen_image_path="background.jpg",
           gravity=-900)

# create ground
ground = game.create_screen_walls(bottom=112, friction=1.0, extra_length=4000)[0]
assert ground, "ground not created"

# create Mario
mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,200), scale_xy=(0.5, 0.5),
                          mass=5, friction=1.0,
                          can_rotate=False)

mario.start_animation(frame_time_s=0.2)
game.camera_follow(mario)

# create platforms
platforms = []
pos = Vec2d(300, 250)
for i in range(500):
    platform = game.create_rect(100, 20, image_path="bricks.png",
                    bottom_left=pos,
                    paint_mode=ImagePaintMode.TILE, scale_xy=(0.5, 0.5),
                    density=1, friction=1.0 fixed_object=True)
    platforms.append(platform)
    pos += Vec2d(random.randint(0, 100), random.randint(-100, 100))
    if pos.y < ground.y():
        pos = Vec2d(pos.x, ground.y() + 100)

# play background music
game.play_sound('music.mp3', loops=-1)

def mario_keyboard(mario, keys):
    grounding = mario.get_grounding()
    well_grounded = False
    ground_velocity = Vec2d(0, 0)
    if grounding.friction < mario.friction:
        well_grounded = True
        ground_velocity = grounding.velocity

    target_horizontal_velocity = 0
    if mario.velocity.x > 0.01:
        direction = 1
    elif mario.velocity.x < -0.01:
        direction = -1

    if "left" in keys:
        direction = -1
        target_horizontal_velocity = -200
        mario.apply_impulse((-1000000, 0))
    elif "right" in keys:
        direction = 1
        target_horizontal_velocity = 200
        mario.apply_impulse((1000000, 0))
    elif "up" in keys:
        if well_grounded:
            jump_velocity = math.sqrt(2.0 * 48 * game.gravity().y)
            impulse = (0, mario.mass * (jump_velocity + ground_velocity.y))
            mario.apply_impulse(impulse)
        game.play_sound('jump.mp3')
    elif "down" in keys:
        direction = -3
        mario.apply_impulse((0, -100000))

    surface_velocity = -target_horizontal_velocity, 0
    if grounding.has_body:
        mario.friction = -200 / 0.05 # player velocity / ground_accel_time
    else:
        mario.friction = 0.0

    # if its in air
    if not grounding.has_body:
        vx = game.interpolate(mario.velocity.x,
                              target_horizontal_velocity + ground_velocity.x,
                              0.05)
        mario.velocity = Vec2d()

game.handle(mario.on_keypress, mario_keyboard)

while game.is_running():
    game.update()