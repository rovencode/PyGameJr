import random
import math
from pygamejr import game, Vec2d, DrawOptions, common


game.start(screen_width=600, screen_height=600,
           screen_color="purple", gravity=-900)

game.create_screen_walls(bottom=False, top=True, left=True, right=True,
                         elasticity=0.7)

r = common.rectangle_from_line(Vec2d(150, 100), Vec2d(50, 550), width=3)
game.create_polygon_any(r, color="grey", elasticity=0.7, fixed_object=True)
r = common.rectangle_from_line(Vec2d(450, 100), Vec2d(550, 550), width=3)
game.create_polygon_any(r, color="grey", elasticity=0.7, fixed_object=True)
r = common.rectangle_from_line(Vec2d(50, 550), Vec2d(300, 600), width=3)
game.create_polygon_any(r, color="grey", elasticity=0.7, fixed_object=True)
r = common.rectangle_from_line(Vec2d(300, 600), Vec2d(50, 550), width=3)
game.create_polygon_any(r, color="grey", elasticity=0.7, fixed_object=True)
r = common.rectangle_from_line(Vec2d(300, 600-180), Vec2d(400, 400), width=3)
game.create_polygon_any(r, color="grey", elasticity=0.7, fixed_object=True)


# create flippers
flipper_points = [Vec2d(20, -20), Vec2d(-120, 0), Vec2d(20, 20)]
centeroid = sum(flipper_points, Vec2d(0, 0)) / len(flipper_points)
flipper_points = [v - centeroid for v in flipper_points]
max_y = max(v.y for v in flipper_points)
flipper_points = [(v.x, max_y-v.y) for v in flipper_points]
right_flipper = game.create_polygon_any(flipper_points, color="green",
                                        center=(450, 100), mass=100,
                                        elasticity=0.4, draw_options=DrawOptions(angle_line_width=1, center_radius=3))
flipper_points = [(-v.x, v.y) for v in right_flipper.shape.get_vertices()]
left_flipper = game.create_polygon_any(flipper_points, color="green",
                                        center=(150, 100), mass=100,
                                        moment=right_flipper.moment,
                                        elasticity=0.4, draw_options=DrawOptions(angle_line_width=1, center_radius=3))

# create pin joints for the flippers
right_flipper_joint = game.create_pin_joint(right_flipper, actor2=right_flipper.position)
left_flipper_joint = game.create_pin_joint(left_flipper, actor2=left_flipper.position)

#attach springs to flippers so they go back to original position
right_flipper_spring = game.create_rotary_spring_joint(right_flipper,
                                                       actor2=right_flipper_joint.b,
                                                       rest_angle=0.15, stiffness=2000000, damping=900000,
                                                       params_as_ratio=False)
left_flipper_spring = game.create_rotary_spring_joint(left_flipper,
                                                    actor2=left_flipper_joint.b,
                                                    rest_angle=-0.15, stiffness=2000000, damping=900000,
                                                    params_as_ratio=False)


def right_flipper_on_keypress(flipper, keys):
    if 'm' in keys:
        flipper.apply_impulse(Vec2d.unit() * -40000, (-100, 0))
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
            current_ball = game.create_circle(25, color="red",
                center=(random.randint(115, 350), 400),
                mass=1, elasticity=0.95)
    game.update()

    # repostion the flippers
    right_flipper.position = Vec2d(450, 100)
    left_flipper.position = Vec2d(150, 100)
    right_flipper.velocity = Vec2d(0, 0)
    left_flipper.velocity = Vec2d(0, 0)

    # remove balls that are off the screen
    if current_ball is not None and current_ball.position.y < 0:
        game.remove(current_ball)
        current_ball = None

game.keep_running()