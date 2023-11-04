from typing import List, Tuple, Optional

import pygame

from pygamejr import utils

running = False
clock = pygame.time.Clock()
screen:Optional[pygame.Surface] = None
actors = []
width, height = 320, 240 #1280, 720 #640, 480 #320, 240
color = "purple"
fps = 60

class Actor:
    def __init__(self, image_path:str, x:int, y:int):
        self.image = pygame.image.load(utils.full_path_abs(image_path))
        self.rect = self.image.get_rect()

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
