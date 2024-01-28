import math
from dataclasses import dataclass
import timeit
from typing import List, Tuple, Optional, Set, Dict, Any, Union, Callable, Iterable
from enum import Enum

import pygame
import pymunk
from pymunk import pygame_util

from pygamejr import utils
from pygamejr import common
from pygamejr.actor import Actor, ActorGroup
from pygamejr.common import PyGameColor

_running = False # is game currently running?

clock = pygame.time.Clock() # game clock
screen:Optional[pygame.Surface] = None # game screen
draw_options:Optional[pygame_util.DrawOptions] = None # pymunk draw options

# pygame setup
pygame.init()
space = pymunk.Space() # physics space

_actors = ActorGroup() # list of all actors
_screen_walls = ActorGroup() # list of all wall
_physics_actors = ActorGroup() # list of all actors with physics enabled
down_keys = set()   # keys currently down
down_mousbuttons = set()  # mouse buttons currently down

# physics
_last_physics_time = 0

@dataclass
class ScreenProps:
    """Screen properties"""
    width:int=1280
    height:int=720
    color:PyGameColor="purple"
    fps:int=60
    image_path:Optional[str]=None
    image:Optional[pygame.Surface]=None # image to display on screen
    image_scaled:Optional[pygame.Surface]=None # scaled image to display on screen
    title:str="PyGameJr Rocks"
_screen_props = ScreenProps()

def is_running()->bool:
    """Is the game currently running?"""
    return _running

def keep_running():
    """
    default game loop
    """
    while _running:
        update()

def handle(event_method:Callable, handler:Callable)->None:
    """
    Assign a handler to a given event method.

    :param event_method: The bound method of the event to handle (e.g., obj.on_keydown).
    :param handler: The handler function to replace the original method.
    """
    if not callable(event_method):
        raise ValueError("The first argument must be a callable method.")

    # Retrieve the self instance from the method
    self = event_method.__self__

    # Get the name of the method
    method_name = event_method.__name__

    # Set the handler to replace the original event method, making sure it's bound
    setattr(self, method_name, handler.__get__(self, type(self)))

def _add_actor(actor:Actor):
    _actors.add(actor)
    if actor.physics.enabled:
        _physics_actors.add(actor)

def create_image(image_path_or_surface:Union[str, Iterable[str], pygame.Surface],
                 x:int, y:int,
                transparent_color:Optional[PyGameColor]=None,
                angle=0.0,
                scale_xy:Tuple[float,float]=(1.0, 1.0),
                enable_transparency:bool=True,
                physics=common.Physics(enabled=False)) -> Actor:

    actor = Actor(x=x, y=y,
                  angle=angle,
                  enable_transparency=enable_transparency,
                  physics=physics)
    _add_actor(actor)

    actor.add_costume_image("", image_path_or_surface,
                            transparent_color=transparent_color,
                            scale_xy=scale_xy)
    actor.set_costume("")

    return actor

def create_rect(width:int=20, height:int=20, x:int=0, y:int=0,
                color:PyGameColor="red", border=0,
                angle=0.0,
                scale_xy:Tuple[float,float]=(1.0, 1.0),
                enable_transparency:bool=True,
                physics=common.Physics(enabled=False)) -> Actor:

    actor = Actor(x=x, y=y,
                  angle=angle,
                  scale_xy=scale_xy,
                  enable_transparency=enable_transparency,
                  physics=physics)
    _add_actor(actor)

    actor.add_costume_rect("", width, height, color, border)
    actor.set_costume("")

    return actor

def create_ellipse(width:int=20, height:int=20, x:int=0, y:int=0,
                color:PyGameColor="yellow", border=0,
                angle=0.0,
                scale_xy:Tuple[float,float]=(1.0, 1.0),
                enable_transparency:bool=True,
                physics=common.Physics(enabled=False)) -> Actor:

    actor = Actor(x=x, y=y,
                  angle=angle,
                  scale_xy=scale_xy,
                  enable_transparency=enable_transparency,
                  physics=physics)
    _add_actor(actor)

    actor.add_costume_ellipse("", width, height, color, border)
    actor.set_costume("")

    return actor

def create_polygon_any(points:List[Tuple[int, int]],
                color:PyGameColor="green", border=0,
                angle=0.0,
                scale_xy:Tuple[float,float]=(1.0, 1.0),
                enable_transparency:bool=True,
                physics=common.Physics(enabled=False)) -> Actor:

    bounding_rect = common.get_bounding_rect(points)
    x, y = bounding_rect.x, bounding_rect.y

    actor = Actor(x=x, y=y,
                  angle=angle,
                  scale_xy=scale_xy,
                  enable_transparency=enable_transparency,
                  physics=physics)
    _add_actor(actor)

    points = [(a - x, b - y) for a, b in points]

    actor.add_costume_polygon_any("", points, color, border)
    actor.set_costume("")

    return actor

def create_polygon(sides:int, width:int=20, height:int=20, x:int=0, y:int=0,
                color:PyGameColor="green", border=0,
                angle=0.0,
                scale_xy:Tuple[float,float]=(1.0, 1.0),
                enable_transparency:bool=True,
                physics=common.Physics(enabled=False)) -> Actor:

    actor = Actor(x=x, y=y,
                  angle=angle,
                  scale_xy=scale_xy,
                  enable_transparency=enable_transparency,
                  physics=physics)
    _add_actor(actor)

    actor.add_costume_polygon("", sides, width, height, color, border)
    actor.set_costume("")

    return actor

def create_screen_walls(left:bool=False, right:bool=False,
                        top:bool=False, bottom:bool=False,
                        color:PyGameColor=(0, 0, 0, 0),
                        border=0,
                        enable_transparency:bool=False,
                        enable_physcs:bool=False):
    global _screen_walls
    physics = common.Physics(enabled=enable_physcs, fixed=True, infinite_wall=True)
    if left:
        actor = create_rect(width=1, height=screen_height(), x=0, y=0, color=color, border=border, enable_transparency=enable_transparency, physics=physics)
        _screen_walls.add(actor)
    if right:
        actor = create_rect(width=1, height=screen_height(), x=screen_width()-border, y=0, color=color, border=border, enable_transparency=enable_transparency, physics=physics)
        _screen_walls.add(actor)
    if top:
        actor = create_rect(width=screen_width(), height=1, x=0, y=0, color=color, border=border, enable_transparency=enable_transparency, physics=physics)
        _screen_walls.add(actor)
    if bottom:
        actor = create_rect(width=screen_width(), height=1, x=0, y=screen_height()-border, color=color, border=border, enable_transparency=enable_transparency, physics=physics)
        _screen_walls.add(actor)

def find_overlap_center(rect1, rect2):
    """ Find the center of the overlapping area of two rectangles """
    overlap = rect1.clip(rect2)
    return pygame.math.Vector2(overlap.center)

def separate_rects(r1, r2):
    r1 = r1.copy()
    r2 = r2.copy()

    ir = r1.clip(r2)
    ir_c = ir.center

    l1 = ir.clipline(ir.center, r1.center)
    ds1 = pygame.math.Vector2(l1[0]) - pygame.math.Vector2(l1[1])

    l2 = ir.clipline(ir.center, r2.center)
    ds2 = pygame.math.Vector2(l2[0]) - pygame.math.Vector2(l2[1])

    # Move the rectangles
    r1.move_ip(-ds1)
    r2.move_ip(-ds2)

    return r1, r2, ir_c

def post_collision_velocities(v1, v2, m1, m2, r1, r2, collision_point):
    # Calculate normal and tangential components of the velocities
    normal1 = (collision_point - pygame.math.Vector2(r1.center)).normalize()
    v1n, v1t = v1.dot(normal1), v1 - v1.dot(normal1) * normal1
    normal2 = (collision_point - pygame.math.Vector2(r2.center)).normalize()
    v2n, v2t = v2.dot(normal2), v2 - v2.dot(normal2) * normal2

    # Apply collision equations - conservation of momentum and kinetic energy
    new_v1n = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
    new_v2n = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

    # Recombine components
    new_v1 = new_v1n * normal1 + v1t
    new_v2 = new_v2n * normal2 + v2t

    # Return the final velocities
    return (new_v1, new_v2)


def apply_physics():
    """
    Apply physics to all actors.
    """
    global _last_physics_time
    if _last_physics_time == 0:
        _last_physics_time = timeit.default_timer()
        return
    dt = timeit.default_timer() - _last_physics_time
    _last_physics_time = timeit.default_timer()

    # Check for collisions within the group
    collisions = pygame.sprite.groupcollide(_physics_actors, _physics_actors, False, False)

    assert len(collisions) == len(_physics_actors), "collisions: {} != _physics_actors: {}".format(len(collisions), len(_physics_actors))
    processed_pairs:Dict[Actor, Set[Actor]] = {actor:set([actor]) for actor in collisions.keys()}
    new_v:Dict[Actor, pygame.math.Vector2] = {actor:pygame.math.Vector2(0, 0) for actor in collisions.keys()}
    new_ds:Dict[Actor, pygame.math.Vector2] = {actor:pygame.math.Vector2(0, 0) for actor in collisions.keys()}
    for sprite, colliding_sprites in collisions.items():
        if len(colliding_sprites) == 1:
            new_v[sprite] += sprite.physics.velocity
        for colliding_sprite in colliding_sprites:
            if colliding_sprite not in processed_pairs[sprite]:
                # r1, r2, cp = separate_rects(sprite.rect, colliding_sprite.rect)
                # r1 = sprite.rect if sprite.physics.fixed else r1
                # r2 = colliding_sprite.rect if colliding_sprite.physics.fixed else r2

                r1, r2 = sprite.rect, colliding_sprite.rect
                cp = find_overlap_center(r1, r2)

                # compute post collision velocities
                vn1, vn2 = post_collision_velocities(sprite.physics.velocity, colliding_sprite.physics.velocity,
                                        sprite.physics.mass, colliding_sprite.physics.mass,
                                        r1, r2, cp)
                new_v[sprite] += vn1
                new_v[colliding_sprite] += vn2
                new_ds[sprite] += pygame.math.Vector2(r1.center) - pygame.math.Vector2(sprite.rect.center)
                new_ds[colliding_sprite] += pygame.math.Vector2(r2.center) - pygame.math.Vector2(colliding_sprite.rect.center)
                processed_pairs[sprite].add(colliding_sprite)
                processed_pairs[colliding_sprite].add(sprite)

        if not sprite.physics.fixed:
            # ds = new_ds[sprite]
            # sprite.rect.move_ip(ds.x, ds.y)

            net_force = sprite.physics.force + _gravity * sprite.physics.mass
            new_v[sprite] += (net_force / sprite.physics.mass) * dt
            ds = new_v[sprite] * dt

            sprite.physics.velocity = new_v[sprite]
            sprite.rect.move_ip(ds.x, ds.y)

def start(screen_title:str=_screen_props.title,
          screen_width=_screen_props.width,
          screen_height=_screen_props.height,
          screen_color:PyGameColor=_screen_props.color,
          screen_image_path:Optional[str]=_screen_props.image_path,
          screen_fps=_screen_props.fps,
          gravity:Optional[float]=None):

    global  _running, screen, draw_options

    set_screen_size(screen_width, screen_height)
    set_screen_color(screen_color)
    set_screen_image(screen_image_path)
    set_screen_fps(screen_fps)
    set_screen_title(screen_title)

    _running = True
    space.gravity = (0.0, -gravity) if gravity is not None else (0.0, 0.0)

    assert screen is not None, "screen is None"
    draw_options = pygame_util.DrawOptions(screen)

def screen_size()->Tuple[int, int]:
    return _screen_props.width, _screen_props.height
def screen_width()->int:
    return _screen_props.width
def screen_height()->int:
    return _screen_props.height
def set_screen_size(width:int, height:int):
    global screen
    screen = pygame.display.set_mode((width, height))
    _screen_props.width = width
    _screen_props.height = height
    _scale_screen_image()

def set_screen_color(color:PyGameColor):
    _screen_props.color = color

def _scale_screen_image():
    if _screen_props.image:
        _screen_props.image_scaled = pygame.transform.scale(_screen_props.image, screen_size())
    else:
        _screen_props.image_scaled = None

def set_screen_image(image_path:Optional[str]):
    if image_path is not None:
        _screen_props.image = common.get_image(image_path)
    else:
        _screen_props.image = None
    _scale_screen_image()
    _screen_props.image_path = image_path

def set_screen_fps(fps:int):
    _screen_props.fps = fps

def set_screen_title(title:str):
    pygame.display.set_caption(title)
    _screen_props.title = title

def on_frame():
    pass

def update():
    global _running

    if not _running:
        return

    # first call physics so manual overrides can happen later
    # use fixed fps for dt instead of actual dt
    space.step(1.0 / _screen_props.fps)

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end()
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            down_keys.add(key_name)
            for actor in _actors:
                actor.on_keydown(key_name)
        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            down_keys.remove(key_name)
            for actor in _actors:
                actor.on_keyup(key_name)
        if event.type == pygame.MOUSEBUTTONDOWN:
            down_mousbuttons.add(event.button)
            for actor in _actors:
                actor.on_mousedown(event.pos, event.button, event.touch)
        if event.type == pygame.MOUSEBUTTONUP:
            down_mousbuttons.remove(event.button)
            for actor in _actors:
                actor.on_mouseup(event.pos, event.button, event.touch)
        if event.type == pygame.MOUSEMOTION:
            for actor in _actors:
                actor.on_mousemove(event.pos)
        if event.type == pygame.MOUSEWHEEL:
            for actor in _actors:
                actor.on_mousewheel(event.pos, event.y)
    if down_keys:
        for actor in _actors:
            actor.on_keypress(down_keys)
    if down_mousbuttons:
        for actor in _actors:
            actor.on_mousebutton(down_mousbuttons)

    # call on_frame() to update your game state
    on_frame()

    assert screen is not None, "screen is None"

    if _screen_props.color:
        screen.fill(_screen_props.color)
    if _screen_props.image_scaled:
        screen.blit(_screen_props.image_scaled, (0, 0))

    _actors.update()
    _actors.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # This will pause the game loop until 1/60 seconds have passed
    # since the last tick. This limits the loop to _running at 60 FPS.
    clock.tick(_screen_props.fps)

def too_left(actor:Actor)->bool:
    return actor.rect.left < 0
def too_right(actor:Actor)->bool:
    return actor.rect.right > screen_size()[0]
def too_top(actor:Actor)->bool:
    return actor.rect.top < 0
def too_bottom(actor:Actor)->bool:
    return actor.rect.bottom > screen_size()[1]

def mouse_xy()->Tuple[int, int]:
    return pygame.mouse.get_pos()

def end():
    global _running

    if _running:
        pygame.quit()
        pygame.display.quit()
        pygame.mixer.quit()
        _running = False
        exit(0)
