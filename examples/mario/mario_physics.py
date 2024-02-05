import random
import math
from pygamejr import game, ImagePaintMode, Vec2d

# constants for how fast Mario can move and jump
PLAYER_VELOCITY = 600
# where is the ground level in image pixels
GROUND_Y = 112

game.start(screen_title="Mario Animation",
           screen_image_path="background.jpg",
           gravity=-900)

game.play_sound('music.mp3')

# create ground
ground = game.create_screen_walls(bottom=GROUND_Y, friction=1.0,
                                  extra_length=20000)[0]

# create Mario
mario = game.create_image(image_path=["mario1.png", "mario2.png", "mario3.png"],
                          bottom_left=(100,200), scale_xy=(0.5, 0.5),
                          mass=5, can_rotate=False)
mario.start_animation()
game.camera_follow_actor(mario)
#game.set_camera_controls(True)


# create platforms
platform1 = game.create_rect(300, 20, image_path="bricks.png",
                bottom_left=(300, 250), paint_mode=ImagePaintMode.TILE,
                scale_xy=(0.5, 0.5),
                density=1, friction=1.0, fixed_object=True)
platform2 = game.create_rect(300, 20, image_path="bricks.png",
                bottom_left=(800, 250), paint_mode=ImagePaintMode.TILE,
                scale_xy=(0.5, 0.5),
                density=1, friction=1.0, fixed_object=True)
platform3 = game.create_rect(300, 20, image_path="bricks.png",
                bottom_left=(1400, 250), paint_mode=ImagePaintMode.TILE,
                scale_xy=(0.5, 0.5),
                density=1, friction=1.0, fixed_object=True)
platform4 = game.create_rect(300, 20, image_path="bricks.png",
                bottom_left=(2000, 250), paint_mode=ImagePaintMode.TILE,
                scale_xy=(0.5, 0.5),
                density=1, friction=1.0, fixed_object=True)

# create hanging ball from platform1 using pin joint
ball = game.create_circle(25, color=game.common.random_color(),
                          center=(300+150, 250-100),
                          density=0.0001, friction=0.2)
game.create_pin_joint(platform1, ball)

# create hanging ball from platform2 using spring joint
ball = game.create_circle(25, color=game.common.random_color(),
                          center=(800+150, 250-100),
                          density=0.0001, friction=0.2)
game.create_spring_joint(platform2, ball)

# create two balls on platform4 and connect them by spring joint
ball1 = game.create_circle(25, color=game.common.random_color(),
                           center=(2000+50, 350),
                           density=0.0001, friction=0.2)
ball2 = game.create_circle(25, color=game.common.random_color(),
                            center=(2000+250, 350),
                            density=0.0001, friction=0.2)
game.create_spring_joint(ball1, ball2)

# create stack of blocks on platform2
for i in range(15):
    game.create_rect(150, 15, color=game.common.random_color(),
                     bottom_left=(800+200, 250 + i*50),
                     density=0.0001, friction=0.3)
    game.create_rect(150, 15, color=game.common.random_color(),
                     bottom_left=(800+200+200, 250 + i*50),
                     density=0.0001, friction=0.3)

 # create bunch of balls on platform3
for i in range(5):
    game.create_circle(25, color=game.common.random_color(),
                       center=(1400+200, 250 + i*50),
                       density=0.0001, friction=0.2, draw_options=game.DrawOptions(angle_line_width=1))

while game.is_running():
    keys = game.key_pressed()

    x_velocity = 0 # Mario's x velocity

    if "left" in keys:
        x_velocity = -PLAYER_VELOCITY
    if "right" in keys:
        x_velocity = PLAYER_VELOCITY
    if "up" in keys:
        jump_velocity = math.sqrt(1.0 * 3 * abs(game.gravity().y))
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