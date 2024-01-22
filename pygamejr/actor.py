from enum import Enum
import math
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

        self.mask:Optional[pygame.mask.Mask] = None
        self.enable_transparency = enable_transparency
        self.rect:pygame.Rect = pygame.Rect(x, y, 0, 0)
        self.costumes:Dict[str, pygame.Surface] = {
            "_hidden_": pygame.Surface((0, 0))
        }
        self.last_shown_costume = self.current_costume = "_hidden_"
        self.angle = 0.0
        self.hide()

    def hide(self):
        if self.current_costume != "_hidden_":
            self.last_shown_costume = self.current_costume
        self.set_costume("_hidden_")

    def is_hidden(self)->bool:
        return self.current_costume == "_hidden_"

    def show(self):
        self.set_costume(self.last_shown_costume)

    def glide_to(self, xy:Tuple[float,float], speed:float=1)->None:
        target_vector = pygame.math.Vector2(xy) - pygame.math.Vector2(self.rect.center)
        if target_vector.length() > 0:
            target_vector = target_vector.normalize() * speed
            new_pos = pygame.math.Vector2(self.rect.center) + target_vector
            self.rect.center = new_pos.x, new_pos.y

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

    def write(self, text:str, font_name:Optional[str]=None, font_size:int=20,
              color:PyGameColor="black", x:int=0, y:int=0,
              background_color:Optional[PyGameColor]=None,
              )->None:

        if text:
            font = pygame.font.Font(font_name, font_size)
            surface = font.render(text, True, color, background_color)

            self.image.blit(surface, (x, y))
        else:
            self.set_costume(self.last_shown_costume)

    def save_current_costume(self, name:str)->None:
        self.costumes[name] = self.image

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
        self.current_costume = name
        if self.angle != 0.0:
            self.turn(self.angle)

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

    def turn(self, angle:float)->None:
        """ Rotate a sprite and keep its center. """
        # Rotate the image
        original_image = self.costumes[self.current_costume]
        self.image = pygame.transform.rotate(original_image, angle)
        # Get the new rect
        self.rect = self.image.get_rect(center=self.rect.center)
        self.angle = angle

    def angle_to(self, xy:Tuple[float,float])->float:
        # Calculate angle to target
        x_diff = xy[0] - self.rect.centerx
        y_diff = xy[1] - self.rect.centery
        angle = math.degrees(math.atan2(-y_diff, x_diff))
        return angle

    def turn_to(self, xy:Tuple[float,float], speed=0.5)->None:
        angle = self.angle_to(xy)*speed
        self.turn(angle)

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
