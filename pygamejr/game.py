import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set, Dict, Any, Union, Callable
from enum import Enum

import pygame

from pygamejr import utils
from pygamejr import common
from pygamejr.actor import Actor, ActorGroup
from pygamejr.common import PyGameColor

_running = False # is game currently running?

clock = pygame.time.Clock() # game clock
screen:Optional[pygame.Surface] = None # game screen

_actors = pygame.sprite.Group() # list of actors
down_keys = set()   # keys currently down
down_mousbuttons = set()  # mouse buttons currently down

@dataclass
class ScreenProps:
    """Screen properties"""
    width:int=1280
    height:int=720
    color:PyGameColor="purple"
    fps:int=60
    image_path:Optional[str]=None
    image:Optional[pygame.Surface]=None # image to display on screen
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


def create_image(image_path_or_surface:Union[str, pygame.Surface], x:int, y:int,
                  transparent_color:Optional[PyGameColor]=None) -> Actor:

    actor = Actor(x=x, y=y)
    _actors.add(actor)

    actor.add_costume_image("", image_path_or_surface, transparent_color)
    actor.set_costume("")

    return actor

def create_rect(width:int=20, height:int=20, x:int=0, y:int=0,
                color:PyGameColor="red", border=0) -> Actor:

    actor = Actor(x=x, y=y)
    _actors.add(actor)

    actor.add_costume_rect("", width, height, color, border)
    actor.set_costume("")

    return actor

def create_ellipse(width:int=20, height:int=20, x:int=0, y:int=0,
                   color:PyGameColor="yellow", border=0) -> Actor:

    actor = Actor(x=x, y=y)
    _actors.add(actor)

    actor.add_costume_ellipse("", width, height, color, border)
    actor.set_costume("")

    return actor

def create_polygon_any(points:List[Tuple[int, int]],
                       color:PyGameColor="green", border=0) -> Actor:

    bounding_rect = common.get_bounding_rect(points)
    x, y = bounding_rect.x, bounding_rect.y

    actor = Actor(x=x, y=y)
    _actors.add(actor)

    points = [(x - x, y - y) for x, y in points]

    actor.add_costume_polygon_any("", points, color, border)
    actor.set_costume("")

    return actor

def create_polygon(sides:int, width:int=20, height:int=20, x:int=0, y:int=0,
                   color:PyGameColor="green", border=0) -> Actor:

    actor = Actor(x=x, y=y)
    _actors.add(actor)

    actor.add_costume_polygon("", sides, width, height, color, border)
    actor.set_costume("")

    return actor

def start(screen_title:str=_screen_props.title,
          screen_width=_screen_props.width,
          screen_height=_screen_props.height,
          screen_color:Optional[str]=_screen_props.color,
          screen_image_path:Optional[str]=_screen_props.image_path,
          screen_fps=_screen_props.fps):

    global  _running

    # pygame setup
    pygame.init()

    set_screen_size(screen_width, screen_height)
    set_screen_color(screen_color)
    set_screen_image(screen_image_path)
    set_screen_fps(screen_fps)
    set_screen_title(screen_title)

    _running = True

def get_screen_size()->Tuple[int, int]:
    return _screen_props.width, _screen_props.height

def set_screen_size(width:int, height:int):
    global screen
    screen = pygame.display.set_mode((width, height))
    _screen_props.width = width
    _screen_props.height = height

def set_screen_color(color:PyGameColor):
    _screen_props.color = color

def set_screen_image(image_path:Optional[str]):
    if image_path is not None:
        _screen_props.image = common.get_image(image_path)
    else:
        _screen_props.image = None
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
    if _screen_props.image:
        screen.blit(_screen_props.image, (0, 0))

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
    return actor.rect.right > get_screen_size()[0]
def too_top(actor:Actor)->bool:
    return actor.rect.top < 0
def too_bottom(actor:Actor)->bool:
    return actor.rect.bottom > get_screen_size()[1]

def end():
    global _running

    if _running:
        pygame.quit()
        pygame.display.quit()
        pygame.mixer.quit()
        _running = False
        exit(0)
