from typing import List, Tuple, Optional, Set

import pygame

from pygamejr import utils

running = False
clock = pygame.time.Clock()
screen:Optional[pygame.Surface] = None
actors = []
width, height = 320, 240 #1280, 720 #640, 480 #320, 240
color = "purple"
fps = 60
down_keys = set()
down_mousbuttons = set()

class Actor:
    def __init__(self, image_path:str, x:int, y:int):
        self.image = pygame.image.load(utils.full_path_abs(image_path))
        self.rect = self.image.get_rect()

    def on_keypress(self, keys:Set[str]):
        pass

    def on_keydown(self, key:str):
        pass

    def on_keyup(self, key:str):
        pass

    def on_mousebutton(self, pos:Tuple[int, int]):
        pass

    def on_mousedown(self, pos:Tuple[int, int]):
        pass

    def on_mouseup(self, pos:Tuple[int, int]):
        pass

    def on_mousemove(self, pos:Tuple[int, int]):
        pass

    def on_mousewheel(self, pos:Tuple[int, int], y:int):
        pass

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
    actor = Actor(image_path, x, y)
    actors.append(actor)
    return actor

def start(screen_color="purple", screen_width=width, screen_height=height, screen_fps=fps):
    global running, dt, screen, width, height, color, fps

    width, height = screen_width, screen_height
    color = screen_color
    fps = screen_fps

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    screen.fill(color)
    running = True

def on_frame():
    pass

def update():
    global running

    if not running:
        return

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end()
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            down_keys.add(key_name)
            for actor in actors:
                actor.on_keydown(key_name)
        if event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)
            down_keys.remove(key_name)
            for actor in actors:
                actor.on_keyup(key_name)
        if event.type == pygame.MOUSEBUTTONDOWN:
            down_mousbuttons.add(event.button)
            for actor in actors:
                actor.on_mousedown(event.pos, event.button, event.touch)
        if event.type == pygame.MOUSEBUTTONUP:
            down_mousbuttons.remove(event.button)
            for actor in actors:
                actor.on_mouseup(event.pos, event.button, event.touch)
        if event.type == pygame.MOUSEMOTION:
            for actor in actors:
                actor.on_mousemove(event.pos)
        if event.type == pygame.MOUSEWHEEL:
            for actor in actors:
                actor.on_mousewheel(event.pos, event.y)
    if down_keys:
        for actor in actors:
            actor.on_keypress(down_keys)
    if down_mousbuttons:
        for actor in actors:
            actor.on_mousebutton(down_mousbuttons)

    # call on_frame() to update your game state
    on_frame()

    assert screen is not None, "screen is None"

    screen.fill(color)
    for actor in actors:
        screen.blit(actor.image, actor.rect)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # This will pause the game loop until 1/60 seconds have passed
    # since the last tick. This limits the loop to running at 60 FPS.
    clock.tick(fps)


def end():
    global running

    if running:
        pygame.quit()
        pygame.display.quit()
        pygame.mixer.quit()
        running = False
        exit(0)
