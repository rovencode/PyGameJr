import random
import math
from pygamejr import game, Vec2d, DrawOptions, common
import pymunk

#game.set_camera_controls(True)
game.start(screen_width=600, screen_height=600,
           screen_color="purple", gravity=-900, physics_fps_multiplier=5, screen_fps=50)

ball_radius = 25
gap_width = ball_radius * 10
right_flipper_center = (300+gap_width/2, 100)
left_flipper_center = (300-gap_width/2, 100)

flipper_points = [(46.7, 40.0), (-93.3, 20.0), (46.7, 0.0)]

game.create_line(left_flipper_center, (50, 550), color="yellow", elasticity=0.7, fixed_object=True, colliision_group=1)
game.create_line(right_flipper_center, (550, 550), color="yellow", elasticity=0.7, fixed_object=True, colliision_group=1)
game.create_line((50, 550), (300, 600), color="yellow", elasticity=0.7, fixed_object=True, colliision_group=1)
game.create_line((300, 600), (550, 550), color="yellow", elasticity=0.7, fixed_object=True, colliision_group=1)
game.create_line(Vec2d(300, 600-180), (400, 400), color="yellow", elasticity=0.7, fixed_object=True, colliision_group=1)

bar = game.create_rect(width=10, height=50, color="magenta", center=(300, 350), mass=1, elasticity=0.7, colliision_group=1,
                                 draw_options=DrawOptions(center_radius=3), friction=0.9)
game.create_pin_joint(bar, actor2=bar.position)

ball1 = game.create_circle(15, color="violet", center=(100, 500), mass=1, elasticity=0.95, colliision_group=1, fixed_object=True)
ball2 = game.create_circle(15, color="violet", center=(100, 450), mass=1, elasticity=0.95, colliision_group=1)
game.create_spring_joint(ball1, actor2=ball2, stiffness=0.9, damping=0.2, rest_length=1.0, params_as_ratio=True)

# create flippers
right_flipper = game.create_polygon_any(flipper_points, color="green",
                                        center=right_flipper_center, mass=100, colliision_group=1,
                                        elasticity=0.4, draw_options=DrawOptions(angle_line_width=1, center_radius=3))
flipper_points = [(-v.x, v.y) for v in right_flipper.shape.get_vertices()]
left_flipper = game.create_polygon_any(flipper_points, color="green",
                                        center=left_flipper_center, mass=100, colliision_group=1,
                                        moment=right_flipper.moment,
                                        elasticity=0.4, draw_options=DrawOptions(angle_line_width=1, center_radius=3))

# create pin joints for the flippers
right_flipper_joint = game.create_pin_joint(right_flipper, actor2=right_flipper.position)
left_flipper_joint = game.create_pin_joint(left_flipper, actor2=left_flipper.position)

#attach springs to flippers so they go back to original position
right_flipper_spring = game.create_rotary_spring_joint(right_flipper,
                                                       actor2=right_flipper_joint.b,
                                                       rest_angle=0.15, stiffness=20000000, damping=900000,
                                                       params_as_ratio=False)
left_flipper_spring = game.create_rotary_spring_joint(left_flipper,
                                                    actor2=left_flipper_joint.b,
                                                    rest_angle=-0.15, stiffness=20000000, damping=900000,
                                                    params_as_ratio=False)


def right_flipper_on_keypress(flipper, keys):
    if 'm' in keys:
        flipper.apply_impulse(Vec2d.unit() * 40000, (-100, 0))
game.handle(right_flipper.on_keypress, right_flipper_on_keypress)

def left_flipper_on_keypress(flipper, keys):
    if 'z' in keys:
        flipper.apply_impulse(Vec2d.unit() * -40000, (-100,0))
game.handle(left_flipper.on_keypress, left_flipper_on_keypress)

current_ball = None
while game.is_running():
    keys = game.key_pressed()
    if 'space' in keys:
        if current_ball is None:
            current_ball = game.create_circle(ball_radius, color="red",
                center=(random.randint(115, 350), 400),
                mass=1, elasticity=0.95)

    # repostion the flippers
    right_flipper.position = Vec2d(*right_flipper_center)
    left_flipper.position = Vec2d(*left_flipper_center)
    right_flipper.velocity = Vec2d(0, 0)
    left_flipper.velocity = Vec2d(0, 0)
    bar.angular_velocity = min(bar.angular_velocity*0.99, 3600)

    # remove balls that are off the screen
    if current_ball is not None and current_ball.position.y < 0:
        game.remove(current_ball)
        current_ball = None

    game.update()


game.keep_running()