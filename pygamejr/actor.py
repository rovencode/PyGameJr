from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import os
from collections.abc import Sequence

import pygame

from pygamejr import utils
from pygamejr import common
from pygamejr.common import PyGameColor

class ActorGroup(pygame.sprite.Group):
    pass

def collide_mask(left:pygame.sprite.Sprite, right:pygame.sprite.Sprite)->bool:
    """collision detection between two sprites, using masks or rectangles.

    pygame.sprite.collide_mask(SpriteLeft, SpriteRight): bool

    Tests for collision between two sprites. If both sprites have a "mask" attribute,
    it tests if their bitmasks overlap. If either sprite does not have a mask,
    it uses rectangle collision detection instead. Sprites must have a "rect" and
    an optional "mask" attribute.

    """
    # Check if both sprites have a mask
    left_has_mask = hasattr(left, 'mask') and left.mask is not None
    right_has_mask = hasattr(right, 'mask') and right.mask is not None

    # If both have masks, use mask collision detection
    if left_has_mask and right_has_mask:
        xoffset = right.rect[0] - left.rect[0]
        yoffset = right.rect[1] - left.rect[1]
        return left.mask.overlap(right.mask, (xoffset, yoffset))

    # Otherwise, use rectangle collision detection
    else:
        return left.rect.colliderect(right.rect)

class Actor(pygame.sprite.Sprite):
    def __init__(self, x:int, y:int, enable_transparency:bool=True):

        super().__init__()

        self.costumes:Dict[str, pygame.Surface] = {}
        self.image = pygame.Surface((0, 0))
        self.rect:pygame.Rect = self.image.get_rect(topleft=(x, y))
        self.mask:Optional[pygame.mask.Mask] = None
        self.enable_transparency = enable_transparency

    def add_costume_image(self, name:str,
                          image_path_or_surface:Union[str, pygame.Surface],
                          transparent_color:Optional[PyGameColor]=None) -> pygame.Surface:

        if isinstance(image_path_or_surface, str):
            image = common.get_image(image_path_or_surface)
            surface = image if image else pygame.Surface((0, 0))
        else:
            surface = image_path_or_surface

        if transparent_color is not None:
            self.image.set_colorkey(transparent_color)
        else:
            if self.enable_transparency and self.has_transparency():
                self.image = self.image.convert_alpha()

        self.costumes[name] = surface
        return surface

    def add_costume_rect(self, name:str,
                         width:int=20, height:int=20,
                         color:PyGameColor="red", border=0) -> pygame.Surface:

        rect:pygame.Rect = pygame.Rect(0, 0, width, height)

        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.rect(surface, color, rect, width=border)

        return self.add_costume_image(name, surface)

    def add_costume_ellipse(self, name:str,
                       width:int=20, height:int=20,
                    color:PyGameColor="yellow", border=0) -> pygame.Surface:
        rect:pygame.Rect = pygame.Rect(0, 0, width, height)
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.ellipse(surface, color, rect, width=border)

        return self.add_costume_image(name, surface)

    def add_costume_polygon_any(self, name:str,
                        points:List[Tuple[int, int]],
                        color:PyGameColor="green", border=0) -> pygame.Surface:
        bounding_rect = common.get_bounding_rect(points)

        # Find the minimum x (left) and y (top) values
        min_x = min(point[0] for point in points)
        min_y = min(point[1] for point in points)

        # Create a new polygon where each point is adjusted by the min_x and min_y
        relative_points = [(x - min_x, y - min_y) for x, y in points]

        surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.polygon(surface, color, relative_points, width=border)

        return self.add_costume_image(name, surface)

    def add_costume_polygon(self, name:str,
                    sides:int, width:int=20, height:int=20,
                    color:PyGameColor="green", border=0) -> pygame.Surface:

        points = common.polygon_points(sides, 0, 0, width, height)
        return self.add_costume_polygon_any(name, points, color, border)

    def set_costume(self, name:str):
        self.image = self.costumes[name]
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

        if self.image.get_colorkey() is not None:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            if self.enable_transparency and self.has_transparency():
                self.mask = pygame.mask.from_surface(self.image)

    def remove_costume(self, name:str):
        del self.costumes[name]

    def move(self, dx:int, dy:int)->pygame.Rect:
        self.rect.move_ip(dx, dy)
        return self.rect

    def has_transparency(self):
        """
        Returns True if the surface has transparency, False otherwise.
        """
        if self.image.get_flags() & pygame.SRCALPHA:
            # Surface is per pixel alpha
            mask = pygame.mask.from_surface(self.image)
            return mask.count() < mask.get_rect().width * mask.get_rect().height
        elif self.image.get_colorkey() is not None:
            # Surface is color key alpha
            return True
        else:
            # No transparency
            return False


    def touches(self, other:Union['Actor', ActorGroup])->Sequence['Actor']:
        if isinstance(other, Actor):
            if pygame.sprite.collide_rect(self, other):
                return [other]
            else:
                return []
        else:
            return pygame.sprite.spritecollide(self, other, False,
                        collide_mask)

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
