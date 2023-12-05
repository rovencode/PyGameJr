import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set, Dict, Any, Union
from enum import Enum

import pygame

from pygamejr import utils
from pygamejr import common
from pygamejr.actor import Actor, ActorType

_running = False # is game currently running?

clock = pygame.time.Clock() # game clock
screen:Optional[pygame.Surface] = None # game screen

_actors = [] # list of actors
down_keys = set()   # keys currently down
down_mousbuttons = set()  # mouse buttons currently down

@dataclass
class ScreenProps:
    width:int=1280
    height:int=720
    color:pygame.ColorValue="purple"
    fps:int=60
    image_path:Optional[str]=None
    image:Optional[pygame.Surface]=None # image to display on screen
    title:str="PyGameJr Rocks"
_screen_props = ScreenProps()

def is_running()->bool:
    return _running

def keep_running():
    """
    default game loop
    """
    while _running:
        update()

def handle(event_method, handler):
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


def create_sprite(image_path:str, x:int, y:int) -> Actor:
    actor = Actor(type=ActorType.image,
                  draw_kwargs={'image_path': image_path, 'x': x, 'y': y})
    _actors.append(actor)
    return actor

def create_rect(width:int=20, height:int=20, x:int=0, y:int=0, color:str="red", border=0) -> Actor:
    actor = Actor(type=ActorType.rect,
                  draw_kwargs={'rect': pygame.Rect(x, y, width, height),
                               'color': color, 'width': border})
    _actors.append(actor)
    return actor

def create_ellipse(width:int=20, height:int=20, x:int=0, y:int=0, color:str="yellow", border=0) -> Actor:
    actor = Actor(type=ActorType.ellipse,
                  draw_kwargs={'rect': pygame.Rect(x, y, width, height),
                               'color': color, 'width': border})
    _actors.append(actor)
    return actor

def create_polygon(sides:int, width:int=20, height:int=20, x:int=0, y:int=0,
                   color:str="green", border=0) -> Actor:
    actor = Actor(type=ActorType.polygon,
                  draw_kwargs={'points': common.polygon_points(sides, x, y, width, height),
                               'color': color, 'width': border})
    _actors.append(actor)
    return actor

def create_line(start_x:int, start_y:int, end_x:int, end_y:int, color:str="red", border=0) -> Actor:
    actor = Actor(type=ActorType.line,
                  draw_kwargs={'start_pos': (start_x, start_y),
                               'end_pos': (end_x, end_y),
                               'color': color, 'width': border})
    _actors.append(actor)
    return actor

def create_polygon_any(points:List[Tuple[int, int]], color:str="green", border=0) -> Actor:
    actor = Actor(type=ActorType.polygon,
                  draw_kwargs={'points': points,
                               'color': color, 'width': border})
    _actors.append(actor)
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

def set_screen_size(width:int, height:int):
    global screen
    screen = pygame.display.set_mode((width, height))
    _screen_props.width = width
    _screen_props.height = height
def set_screen_color(color:pygame.ColorValue):
    global screen
    screen.fill(color)
    _screen_props.color = color
def set_screen_image(image_path:Optional[str]):
    global screen_image
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

    if color:
        screen.fill(color)
    if screen_image:
        screen.blit(screen_image, (0, 0))

    for actor in _actors:
        actor.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # This will pause the game loop until 1/60 seconds have passed
    # since the last tick. This limits the loop to _running at 60 FPS.
    clock.tick(fps)


def end():
    global _running

    if _running:
        pygame.quit()
        pygame.display.quit()
        pygame.mixer.quit()
        _running = False
        exit(0)
