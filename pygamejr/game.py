import math
from dataclasses import dataclass
import timeit
from typing import List, Tuple, Optional, Set, Dict, Any, Union, Callable, Iterable, Sequence
from enum import Enum
import time

import pygame
import pymunk
from pymunk import pygame_util, Vec2d

from pygamejr import utils
from pygamejr import common
from pygamejr.actor import Actor
from pygamejr.common import PyGameColor, DrawOptions, Coordinates, Vector2

TRANSPARENT_COLOR = (0, 0, 0, 0)

_running = False # is game currently running?
show_mouse_coordinates = False # show mouse coordinates in console?

clock = pygame.time.Clock() # game clock
screen:Optional[pygame.Surface] = None # game screen
draw_options:Optional[pygame_util.DrawOptions] = None # pymunk draw options

# For y flip conversion between pymunk and pygame coordinates
pygame_util.positive_y_is_up = True

# pygame setup
pygame.init()
space = pymunk.Space() # physics space

_actors = [] # list of all actors
_screen_walls = [] # list of all wall
down_keys = set()   # keys currently down
down_mousbuttons = set()  # mouse buttons currently down

_default_poly_radius = 1

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


def create_image(image_path:Union[str, Iterable[str]],
                bottom_left:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    if isinstance(image_path, str):
        image_path = [image_path]
    else:
        image_path = list(image_path)
    image = common.get_image(image_path[0])

    width, height = image.get_size()
    if scale_xy is not None:
        width, height = width*scale_xy[0], height*scale_xy[1]

    body_type = pymunk.Body.KINEMATIC if density == 0.0 else pymunk.Body.DYNAMIC
    if unmoveable:
        body_type = pymunk.Body.STATIC

    body = pymunk.Body(body_type=body_type)
    body.position = bottom_left[0] + width/2., bottom_left[1] + height/2.
    body.angle = angle
    body.velocity = Vec2d(*velocity)
    body.angular_velocity = math.radians(angular_velocity)

    shape = pymunk.Poly.create_box(body,
                                   size=(width, height),
                                   radius=_default_poly_radius)
    shape.density = density
    shape.elasticity = elasticity
    shape.friction = friction

    space.add(body, shape)

    actor = Actor(shape=shape,
                  border=border,
                  color=(0, 0, 0, 0),
                  image_paths=image_path,
                  image_scale_xy=scale_xy,
                  image_transparent_color=transparent_color,
                  image_transparency_enabled=transparency_enabled,
                  image_shape_crop=shape_crop,
                  visible=visible,
                  draw_options=draw_options,)

    _actors.append(actor)

    return actor

def create_rect(width:int=20, height:int=20,
                color:PyGameColor="red",
                image_path:Union[str, Iterable[str]]=[],
                bottom_left:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    body_type = pymunk.Body.KINEMATIC if density == 0.0 else pymunk.Body.DYNAMIC
    if unmoveable:
        body_type = pymunk.Body.STATIC

    # shape center is at (0,0)
    r_bottom_left = Vec2d(-width/2., -height/2.)

    body = pymunk.Body(body_type=body_type)
    offset = Vec2d(*bottom_left) - r_bottom_left
    body.position = offset # centroid is now zero so no need to add to offset
    body.angle = angle
    body.velocity = Vec2d(*velocity)
    body.angular_velocity = math.radians(angular_velocity)

    shape = pymunk.Poly.create_box(body,
                                   size=(width, height),
                                   radius=_default_poly_radius)
    shape.density = density
    shape.elasticity = elasticity
    shape.friction = friction

    space.add(body, shape)

    actor = Actor(shape=shape,
                  color=color,
                  border=border,
                  image_paths=image_path,
                  image_scale_xy=scale_xy,
                  image_transparent_color=transparent_color,
                  image_transparency_enabled=transparency_enabled,
                  image_shape_crop=shape_crop,
                  visible=visible,
                  draw_options=draw_options,)

    _actors.append(actor)

    return actor

def create_circle(radius:float=20,
                color:PyGameColor="red",
                image_path:Union[str, Iterable[str]]=[],
                center:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    body_type = pymunk.Body.KINEMATIC if density == 0.0 else pymunk.Body.DYNAMIC
    if unmoveable:
        body_type = pymunk.Body.STATIC

    body = pymunk.Body(body_type=body_type)
    body.position = center
    body.angle = angle
    body.velocity = Vec2d(*velocity)
    body.angular_velocity = math.radians(angular_velocity)

    shape = pymunk.Circle(body, radius)
    shape.density = density
    shape.elasticity = elasticity
    shape.friction = friction

    space.add(body, shape)

    actor = Actor(shape=shape,
                  color=color,
                  border=border,
                  image_paths=image_path,
                  image_scale_xy=scale_xy,
                  image_transparent_color=transparent_color,
                  image_transparency_enabled=transparency_enabled,
                  image_shape_crop=shape_crop,
                  visible=visible,
                  draw_options=draw_options,)

    _actors.append(actor)

    return actor

def create_ellipse(width:int=20, height:int=20,
                color:PyGameColor="red",
                image_path:Union[str, Iterable[str]]=[],
                bottom_left:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    body_type = pymunk.Body.KINEMATIC if density == 0.0 else pymunk.Body.DYNAMIC
    if unmoveable:
        body_type = pymunk.Body.STATIC

    body = pymunk.Body(body_type=body_type)
    body.position = bottom_left[0] + width/2., bottom_left[1] + height/2.
    body.angle = angle
    body.velocity = Vec2d(*velocity)
    body.angular_velocity = math.radians(angular_velocity)

    shape = pymunk.Poly.create_box(body,
                                   size=(width, height),
                                   radius=_default_poly_radius)
    shape.density = density
    shape.elasticity = elasticity
    shape.friction = friction

    space.add(body, shape)

    actor = Actor(shape=shape,
                  color=color,
                  border=border,
                  image_paths=image_path,
                  image_scale_xy=scale_xy,
                  image_transparent_color=transparent_color,
                  image_transparency_enabled=transparency_enabled,
                  image_shape_crop=shape_crop,
                  visible=visible,
                  draw_options=draw_options,)

    _actors.append(actor)

    return actor


def create_polygon_any(points:Sequence[Coordinates],
                color:PyGameColor="red",
                image_path:Union[str, Iterable[str]]=[],
                bottom_left:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    body_type = pymunk.Body.KINEMATIC if density == 0.0 else pymunk.Body.DYNAMIC
    if unmoveable:
        body_type = pymunk.Body.STATIC

    centroid = sum(points, Vec2d(0., 0.))
    centroid = Vec2d(centroid[0]/len(points), centroid[1]/len(points))
    # let the center be the origin
    points = [Vec2d(*p) - centroid for p in points]

    # new centroid i snow at (0,0)

    r = common.get_bounding_rect(points)
    r_bottom_left = Vec2d(r[2], r[3])

    body = pymunk.Body(body_type=body_type)
    offset = Vec2d(*bottom_left) - r_bottom_left
    body.position = offset # centroid is now zero so no need to add to offset
    body.angle = angle
    body.velocity = Vec2d(*velocity)
    body.angular_velocity = math.radians(angular_velocity)

    shape = pymunk.Poly(body, points, radius=_default_poly_radius)
    shape.density = density
    shape.elasticity = elasticity
    shape.friction = friction

    space.add(body, shape)

    actor = Actor(shape=shape,
                  color=color,
                  border=border,
                  image_paths=image_path,
                  image_scale_xy=scale_xy,
                  image_transparent_color=transparent_color,
                  image_transparency_enabled=transparency_enabled,
                  image_shape_crop=shape_crop,
                  visible=visible,
                  draw_options=draw_options,)

    _actors.append(actor)

    return actor

def create_polygon(sides:int, width:int=20, height:int=20,
                color:PyGameColor="red",
                image_path:Union[str, Iterable[str]]=[],
                bottom_left:Coordinates=(0, 0),
                angle=0.0, border=0,
                transparent_color:Optional[PyGameColor]=None,
                scale_xy:Tuple[float,float]=(1., 1.),
                transparency_enabled:bool=True,
                shape_crop:bool=True,
                draw_options:Optional[DrawOptions]=None,
                visible:bool=True,
                density=0.0, elasticity=1.0, friction=0.0, unmoveable=False,
                velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> Actor:

    points = common.polygon_points(sides, 0, 0, width, height)

    return create_polygon_any(points=points,
                color=color,
                image_path=image_path,
                bottom_left=bottom_left,
                angle=angle, border=border,
                transparent_color=transparent_color,
                scale_xy=scale_xy,
                transparency_enabled=transparency_enabled,
                shape_crop=shape_crop,
                draw_options=draw_options,
                visible=visible,
                density=density, elasticity=elasticity, friction=friction, unmoveable=unmoveable,
                velocity=velocity, angular_velocity=angular_velocity)

def create_screen_walls(left:Optional[Union[float, bool]]=None,
                        right:Optional[Union[float, bool]]=None,
                        top:Optional[Union[float, bool]]=None,
                        bottom:Optional[Union[float, bool]]=None,
                        color:PyGameColor=(0, 0, 0, 0),
                        border=0,
                        transparency_enabled:bool=False,
                        density=1.0, elasticity=1.0, friction=0.0, unmoveable=True,
                        velocity:Vector2=Vec2d.zero(), angular_velocity:float=0.) -> None:
    global _screen_walls

    left = (0. if left else None) if isinstance(left, bool) else left
    right = (0. if right else None) if isinstance(right, bool) else right
    top = (0. if top else None) if isinstance(top, bool) else top
    bottom = (0. if bottom else None) if isinstance(bottom, bool) else bottom

    if left is not None:
        actor = create_rect(width=1, height=screen_height(),
                            bottom_left=(left, 0),
                            color=color, border=border,
                            transparency_enabled=transparency_enabled,
                            density=density, elasticity=elasticity, friction=friction, unmoveable=unmoveable,
                            velocity=velocity, angular_velocity=angular_velocity)
        _screen_walls.append(actor)
    if right is not None:
        actor = create_rect(width=1, height=screen_height(),
                            bottom_left=(screen_width()-right, 0),
                            color=color, border=border,
                            transparency_enabled=transparency_enabled,
                            density=density, elasticity=elasticity, friction=friction, unmoveable=unmoveable,
                            velocity=velocity, angular_velocity=angular_velocity)
        _screen_walls.append(actor)
    if top is not None:
        actor = create_rect(width=screen_width(), height=1,
                            bottom_left=(0, screen_height()-top),
                            color=color, border=border,
                            transparency_enabled=transparency_enabled,
                            density=density, elasticity=elasticity, friction=friction, unmoveable=unmoveable,
                            velocity=velocity, angular_velocity=angular_velocity)
        _screen_walls.append(actor)
    if bottom is not None:
        actor = create_rect(width=screen_width(), height=1,
                            bottom_left=(0, bottom),
                            color=color, border=border,
                            transparency_enabled=transparency_enabled,
                            density=density, elasticity=elasticity, friction=friction, unmoveable=unmoveable,
                            velocity=velocity, angular_velocity=angular_velocity)
        _screen_walls.append(actor)


def start(screen_title:str=_screen_props.title,
          screen_width=_screen_props.width,
          screen_height=_screen_props.height,
          screen_color:PyGameColor=_screen_props.color,
          screen_image_path:Optional[str]=_screen_props.image_path,
          screen_fps=_screen_props.fps,
          gravity:Optional[Union[float, Vector2]]=None):

    global  _running, screen, draw_options

    set_screen_size(screen_width, screen_height)
    set_screen_color(screen_color)
    set_screen_image(screen_image_path)
    set_screen_fps(screen_fps)
    set_screen_title(screen_title)

    _running = True

    if gravity is not None:
        if not isinstance(gravity, Iterable):
            gravity = (0.0, gravity)
        space.gravity = Vec2d(*gravity)

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
    global _running, _wait_for

    if not _running or _wait_for > timeit.default_timer():
        return
    _wait_for = 0

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

    for actor in _actors:
        actor.update()
    for actor in _actors:
        actor.draw(screen)

    if show_mouse_coordinates:
        common.print_to(screen, f'{mouse_xy()}')

    # flip() the display to put your work on screen
    pygame.display.flip()

    # This will pause the game loop until 1/60 seconds have passed
    # since the last tick. This limits the loop to _running at 60 FPS.
    clock.tick(_screen_props.fps)

def too_left(actor:Actor)->bool:
    return actor.left() < 0
def too_right(actor:Actor)->bool:
    return actor.right() > screen_width()
def too_top(actor:Actor)->bool:
    return actor.top() > screen_height()
def too_bottom(actor:Actor)->bool:
    return actor.bottom() < 0

def mouse_xy()->Tuple[int, int]:
    assert screen is not None, "screen is None"
    return pygame_util.from_pygame(pygame.mouse.get_pos(), screen)

def end():
    global _running

    if _running:
        pygame.quit()
        pygame.display.quit()
        pygame.mixer.quit()
        _running = False
        exit(0)

def wait(seconds:float, reset=False):
    """
    Pause the game for the given number of seconds.
    """
    if _wait_for == 0 or reset:
        global _wait_for
        _wait_for = timeit.default_timer() + seconds