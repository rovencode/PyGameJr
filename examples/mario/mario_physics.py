import random
import math
from pygamejr import game, ImagePaintMode, Vec2d

# constants for how fast Mario can move and jump
PLAYER_VELOCITY = 800
# where is the ground level in image pixels
GROUND_Y = 112

game.set_camera_controls(True)
game.start(screen_title="Mario Animation",
           screen_image_path="background.jpg",
           gravity=-900)

# create ground
ground = game.create_screen_walls(bottom=GROUND_Y, friction=1.0,
                                  extra_length=20000)[0]

# create Mario
mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,200), scale_xy=(0.5, 0.5),
                          mass=5, can_rotate=False)
mario.start_animation()
game.camera_follow_actor(mario)

# create platforms
platforms = []
pos = Vec2d(300, 250)
for i in range(2):
    platform = game.create_rect(300, 20, image_path="bricks.png",
                    bottom_left=pos, paint_mode=ImagePaintMode.TILE,
                    scale_xy=(0.5, 0.5),
                    density=1, friction=1.0, fixed_object=True)
    platforms.append(platform)
    pos += Vec2d(random.randint(300, 800), random.randint(-100, 100))
    if pos.y < GROUND_Y:
        pos = Vec2d(pos.x, GROUND_Y + 100)

# play background music
#game.play_sound('music.mp3', loops=-1)

while game.is_running():
    keys = game.key_pressed()

    x_velocity = 0 # Mario's x velocity

    if "left" in keys:
        x_velocity = -PLAYER_VELOCITY
    if "right" in keys:
        x_velocity = PLAYER_VELOCITY
    if "up" in keys:
        jump_velocity = math.sqrt(1.0 * 48 * abs(game.gravity().y))
        impulse = (0, mario.mass * (jump_velocity))
        mario.apply_impulse(impulse)
        game.play_sound('jump.mp3')

    # set Mario's x velocity
    mario.surface_velocity = Vec2d(x_velocity, mario.surface_velocity.y)


    mario.velocity = Vec2d(game.common.interpolate(mario.velocity.x,
                                                    x_velocity,
                                                    PLAYER_VELOCITY * 1./game.screen_fps()),
                            mario.velocity.y)

    #clamp Mario's velocity
    mario.velocity = Vec2d(
        mario.velocity.x,
        game.common.clamp(mario.velocity.y, -PLAYER_VELOCITY, PLAYER_VELOCITY))

    game.update()