import math
from typing import List, Tuple, Optional, Set, Dict, Any, Union
from enum import Enum

import pygame

from pygamejr import utils

running = False
clock = pygame.time.Clock()
screen:Optional[pygame.Surface] = None
actors = []
width, height = 320, 240 #1280, 720 #640, 480 #320, 240
color = "purple"
screen_image:Optional[pygame.Surface] = None
fps = 60
down_keys = set()
down_mousbuttons = set()
images = {}

def get_image(image_path:Optional[str], cache=True):
    if image_path is None:
        return None
    if image_path not in images:
        image = pygame.image.load(utils.full_path_abs(image_path))
        if cache:
            images[image_path] = image
    else:
        image = images[image_path]
    return image

class ActorType(Enum):
    image = 'image'
    rect = 'rect'
    ellipse = 'ellipse'
    polygon = 'polygon'
    line = 'line'

def polygon_points(sides:int, left:int, top:int, polygon_width:int, polygon_height:int):
    # The distance from the center to a corner (radius)
    radius_x = polygon_width / 2
    radius_y = polygon_height / 2

    # Calculate the center of the polygon
    center_x = left + radius_x
    center_y = top + radius_y

    # Calculate the points of the polygon
    polygon_points = []
    for i in range(sides):
        angle = math.radians(360 / sides * i - 90)  # Subtract 90 degrees to start from the top
        x = center_x + radius_x * math.cos(angle)
        y = center_y + radius_y * math.sin(angle)
        polygon_points.append((x, y))

    return polygon_points

def get_bounding_rect(polygon_points:List[Tuple[int, int]])->pygame.Rect:
    # Unzip the polygon points into two separate lists of x coordinates and y coordinates
    x_coordinates, y_coordinates = zip(*polygon_points)

    # Use min and max to find the bounding coordinates
    top_left_x = min(x_coordinates)
    top_left_y = min(y_coordinates)
    bottom_right_x = max(x_coordinates)
    bottom_right_y = max(y_coordinates)

    # Create a pygame.Rect representing the bounding rectangle
    # The width and height are calculated by subtracting the top left from the bottom right coordinates
    bounding_rect = pygame.Rect(top_left_x, top_left_y, bottom_right_x - top_left_x, bottom_right_y - top_left_y)

    return bounding_rect

def keep_running():
    while running:
        update()

class Actor:
    def __init__(self, type:ActorType, draw_kwargs:Dict[str, Any]):
        self.type = type
        self.draw_kwargs = draw_kwargs
        self.surface, self.x, self.y = self.create_surface()

    def create_surface(self)->Tuple[pygame.Surface, int, int]:
        if self.type == ActorType.image:
            image = get_image(self.draw_kwargs['image_path'])
            surface = image if image else pygame.Surface((0, 0))
            x, y = self.draw_kwargs['x'], self.draw_kwargs['y']

        elif self.type == ActorType.rect:
            rect:pygame.Rect = self.draw_kwargs['rect'].copy()
            rect.topleft = (0, 0)

            surface = pygame.Surface((self.draw_kwargs['rect'].width, self.draw_kwargs['rect'].height))
            pygame.draw.rect(surface, self.draw_kwargs['color'],
                             rect,
                             width=self.draw_kwargs.get('width', 0))
            x, y = self.draw_kwargs['rect'].x, self.draw_kwargs['rect'].y

        elif self.type == ActorType.ellipse:
            rect:pygame.Rect = self.draw_kwargs['rect'].copy()
            rect.topleft = (0, 0)

            surface = pygame.Surface((self.draw_kwargs['rect'].width, self.draw_kwargs['rect'].height), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0)) # transparent color
            pygame.draw.ellipse(surface, self.draw_kwargs['color'],
                                rect,
                                width=self.draw_kwargs.get('width', 0))
            x, y = self.draw_kwargs['rect'].x, self.draw_kwargs['rect'].y

        elif self.type == ActorType.polygon:
            bounding_rect = get_bounding_rect(self.draw_kwargs['points'])

            # Find the minimum x (left) and y (top) values
            min_x = min(point[0] for point in self.draw_kwargs['points'])
            min_y = min(point[1] for point in self.draw_kwargs['points'])

            # Create a new polygon where each point is adjusted by the min_x and min_y
            relative_points = [(x - min_x, y - min_y) for x, y in self.draw_kwargs['points']]

            surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0)) # transparent color
            pygame.draw.polygon(surface, self.draw_kwargs['color'],
                                relative_points,
                                width=self.draw_kwargs.get('width', 0))

            x, y = bounding_rect.x, bounding_rect.y

        elif self.type == ActorType.line:
            points = [self.draw_kwargs['start_pos'], self.draw_kwargs['end_pos']]
            bounding_rect = get_bounding_rect(points)

            # Find the minimum x (left) and y (top) values
            min_x = min(point[0] for point in points)
            min_y = min(point[1] for point in points)

            # Create a new polygon where each point is adjusted by the min_x and min_y
            relative_points = [(x - min_x, y - min_y) for x, y in points]

            surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0)) # transparent color
            pygame.draw.line(surface, self.draw_kwargs['color'],
                             relative_points[0],
                             relative_points[1],
                             width=self.draw_kwargs.get('width', 0))

            x, y = bounding_rect.x, bounding_rect.y
        else:
            raise ValueError("Invalid ActorType: %s" % self.type)

        return surface, x, y

    def set_color(self, color:str):
        self.draw_kwargs['color'] = color

    def set_border(self, border:int):
        self.draw_kwargs['width'] = border

    def move(self, dx:int, dy:int)->Tuple[int, int]:
        if self.type == ActorType.image:
            self.draw_kwargs['x'] += dx
            self.draw_kwargs['y'] += dy
            return self.draw_kwargs['x'], self.draw_kwargs['y']
        elif self.type == ActorType.rect:
            self.draw_kwargs['rect'].move_ip(dx, dy)
            return self.draw_kwargs['rect'].x, self.draw_kwargs['rect'].y
        elif self.type == ActorType.ellipse:
            self.draw_kwargs['rect'].move_ip(dx, dy)
            return self.draw_kwargs['rect'].x, self.draw_kwargs['rect'].y
        elif self.type == ActorType.polygon:
            self.draw_kwargs['points'] = [(x + dx, y + dy) for x, y in self.draw_kwargs['points']]
            # return min x, min y
            return get_bounding_rect(self.draw_kwargs['points']).topleft
        elif self.type == ActorType.line:
            self.draw_kwargs['start_pos'] = (self.draw_kwargs['start_pos'][0] + dx,
                                             self.draw_kwargs['start_pos'][1] + dy)
            self.draw_kwargs['end_pos'] = (self.draw_kwargs['end_pos'][0] + dx,
                                           self.draw_kwargs['end_pos'][1] + dy)
            return self.draw_kwargs['start_pos']
        else:
            raise ValueError("Invalid ActorType: %s" % self.type)

    def touches(self, other:Union['Actor', List['Actor']])->bool:
        if isinstance(other, list):
            return self.rect().collidelist([o.rect() for o in other]) != -1
        else:
            return self.rect().colliderect(other.rect())

    def rect(self)->pygame.Rect:
        if self.type == ActorType.image:
            image = get_image(self.draw_kwargs['image_path'])
            if image:
                return image.get_rect().move(self.draw_kwargs['x'], self.draw_kwargs['y'])
        elif self.type == ActorType.rect:
            return pygame.Rect(self.draw_kwargs['rect'])
        elif self.type == ActorType.ellipse:
            return pygame.Rect(self.draw_kwargs['rect'])
        elif self.type == ActorType.polygon:
            return get_bounding_rect(self.draw_kwargs['points'])
        elif self.type == ActorType.line:
            return pygame.Rect(self.draw_kwargs['start_pos'],
                               self.draw_kwargs['end_pos'])
        return pygame.Rect(0, 0, 0, 0)

    def draw(self, screen:pygame.Surface):
        if self.type == ActorType.image:
            image = get_image(self.draw_kwargs['image_path'])
            if image:
                screen.blit(image, (self.draw_kwargs['x'], self.draw_kwargs['y']))
        elif self.type == ActorType.rect:
            pygame.draw.rect(screen, self.draw_kwargs['color'],
                             self.draw_kwargs['rect'],
                             width=self.draw_kwargs.get('width', 0))
        elif self.type == ActorType.ellipse:
            pygame.draw.ellipse(screen, self.draw_kwargs['color'],
                                self.draw_kwargs['rect'],
                                width=self.draw_kwargs.get('width', 0))
        elif self.type == ActorType.polygon:
            pygame.draw.polygon(screen, self.draw_kwargs['color'],
                                self.draw_kwargs['points'],
                                width=self.draw_kwargs.get('width', 0))
        elif self.type == ActorType.line:
            pygame.draw.line(screen, self.draw_kwargs['color'],
                             self.draw_kwargs['start_pos'],
                             self.draw_kwargs['end_pos'],
                             width=self.draw_kwargs.get('width', 0))
        else:
            raise ValueError("Invalid ActorType: %s" % self.type)

    def on_keypress(self, keys:Set[str]):
        pass

    def on_keydown(self, key:str):
        pass

    def on_keyup(self, key:str):
        pass

    def on_mousebutton(self, pos:Tuple[int, int]):
        pass

    def on_mousedown(self, pos:Tuple[int, int], button:int, touch:Optional[int]):
        pass

    def on_mouseup(self, pos:Tuple[int, int], button:int, touch:Optional[int]):
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
    actor = Actor(type=ActorType.image,
                  draw_kwargs={'image_path': image_path, 'x': x, 'y': y})
    actors.append(actor)
    return actor

def create_rect(width:int=20, height:int=20, x:int=0, y:int=0, color:str="red", border=0) -> Actor:
    actor = Actor(type=ActorType.rect,
                  draw_kwargs={'rect': pygame.Rect(x, y, width, height),
                               'color': color, 'width': border})
    actors.append(actor)
    return actor

def create_ellipse(width:int=20, height:int=20, x:int=0, y:int=0, color:str="yellow", border=0) -> Actor:
    actor = Actor(type=ActorType.ellipse,
                  draw_kwargs={'rect': pygame.Rect(x, y, width, height),
                               'color': color, 'width': border})
    actors.append(actor)
    return actor

def create_polygon(sides:int, width:int=20, height:int=20, x:int=0, y:int=0,
                   color:str="green", border=0) -> Actor:
    actor = Actor(type=ActorType.polygon,
                  draw_kwargs={'points': polygon_points(sides, x, y, width, height),
                               'color': color, 'width': border})
    actors.append(actor)
    return actor

def create_line(start_x:int, start_y:int, end_x:int, end_y:int, color:str="red", border=0) -> Actor:
    actor = Actor(type=ActorType.line,
                  draw_kwargs={'start_pos': (start_x, start_y),
                               'end_pos': (end_x, end_y),
                               'color': color, 'width': border})
    actors.append(actor)
    return actor

def create_polygon_any(points:List[Tuple[int, int]], color:str="green", border=0) -> Actor:
    actor = Actor(type=ActorType.polygon,
                  draw_kwargs={'points': points,
                               'color': color, 'width': border})
    actors.append(actor)
    return actor

def is_running()->bool:
    return running

def start(title:Optional[str]=None, screen_width=width, screen_height=height,
          screen_color:Optional[str]="purple",
          screen_image_path:Optional[str]=None,
          screen_fps=fps):

    global running, dt, screen, width, height, color, fps, screen_image

    width, height = screen_width, screen_height
    color = screen_color
    fps = screen_fps

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    if title:
        pygame.display.set_caption(title)

    if color:
        screen.fill(color)
    if screen_image_path:
        screen_image = get_image(screen_image_path)

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

    if color:
        screen.fill(color)
    if screen_image:
        screen.blit(screen_image, (0, 0))

    for actor in actors:
        actor.draw(screen)

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
