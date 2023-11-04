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

class Actor:
    def __init__(self, image_path:str, x:int, y:int):
        self.image = pygame.image.load(utils.full_path_abs(image_path))
        self.rect = self.image.get_rect()

    def on_keyboard(self, keys:Set[str]):
        pass

    def attach_on_keyboard(self, callback):
        self.on_keyboard = callback.__get__(self)

    def on_keydown(self, key:str):
        pass

    def attach_on_keydown(self, callback):
        self.on_keydown = callback.__get__(self)

    def on_keyup(self, key:str):
        pass

    def attach_on_keyup(self, callback):
        self.on_keyup = callback.__get__(self)

    def on_mousedown(self, pos:Tuple[int, int]):
        pass

    def attach_on_mousedown(self, callback):
        self.on_mousedown = callback.__get__(self)

    def on_mouseup(self, pos:Tuple[int, int]):
        pass

    def attach_on_mouseup(self, callback):
        self.on_mouseup = callback.__get__(self)

    def on_mousemove(self, pos:Tuple[int, int]):
        pass

    def attach_on_mousemove(self, callback):
        self.on_mousemove = callback.__get__(self)

    def on_mousewheel(self, pos:Tuple[int, int], y:int):
        pass

    def attach_on_mousewheel(self, callback):
        self.on_mousewheel = callback.__get__(self)



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


def rest():
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
            for actor in actors:
                actor.on_mousedown(event.pos)
        if event.type == pygame.MOUSEBUTTONUP:
            for actor in actors:
                actor.on_mouseup(event.pos)
        if event.type == pygame.MOUSEMOTION:
            for actor in actors:
                actor.on_mousemove(event.pos)
        if event.type == pygame.MOUSEWHEEL:
            for actor in actors:
                actor.on_mousewheel(event.pos, event.y)
    if down_keys:
        for actor in actors:
            actor.on_keyboard(down_keys)


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
