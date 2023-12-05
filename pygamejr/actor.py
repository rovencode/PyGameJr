from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import os
import pygame

from pygamejr import utils
from pygamejr import common

class ActorType(Enum):
    image = 'image'
    rect = 'rect'
    ellipse = 'ellipse'
    polygon = 'polygon'
    line = 'line'


class Actor:
    def __init__(self, type:ActorType, draw_kwargs:Dict[str, Any]):
        self.type = type
        self.draw_kwargs = draw_kwargs
        self.surface, self.x, self.y = self.create_surface()

    def create_surface(self)->Tuple[pygame.Surface, int, int]:
        if self.type == ActorType.image:
            image = common.get_image(self.draw_kwargs['image_path'])
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
            bounding_rect = common.get_bounding_rect(self.draw_kwargs['points'])

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
            bounding_rect = common.get_bounding_rect(points)

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
            return common.get_bounding_rect(self.draw_kwargs['points']).topleft
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
            image = common.get_image(self.draw_kwargs['image_path'])
            if image:
                return image.get_rect().move(self.draw_kwargs['x'], self.draw_kwargs['y'])
        elif self.type == ActorType.rect:
            return pygame.Rect(self.draw_kwargs['rect'])
        elif self.type == ActorType.ellipse:
            return pygame.Rect(self.draw_kwargs['rect'])
        elif self.type == ActorType.polygon:
            return common.get_bounding_rect(self.draw_kwargs['points'])
        elif self.type == ActorType.line:
            return pygame.Rect(self.draw_kwargs['start_pos'],
                               self.draw_kwargs['end_pos'])
        return pygame.Rect(0, 0, 0, 0)

    def draw(self, screen:pygame.Surface):
        if self.type == ActorType.image:
            image = common.get_image(self.draw_kwargs['image_path'])
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
