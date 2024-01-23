from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable
from dataclasses import dataclass, fields
from enum import Enum
import math
import os
from collections.abc import Sequence
import timeit

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
    left_has_mask = hasattr(left, 'mask') and left.mask is not None # type: ignore
    right_has_mask = hasattr(right, 'mask') and right.mask is not None # type: ignore

    # If both have masks, use mask collision detection
    if left_has_mask and right_has_mask:
        xoffset = right.rect[0] - left.rect[0] # type: ignore
        yoffset = right.rect[1] - left.rect[1] # type: ignore
        return left.mask.overlap(right.mask, (xoffset, yoffset)) # type: ignore

    # Otherwise, use rectangle collision detection
    else:
        return left.rect.colliderect(right.rect) # type: ignore

COSTUME_ZERO = "_hidden_"

@dataclass
class TextInfo:
    text:str
    font_name:Optional[str]=None
    font_size:int=20
    color:PyGameColor="black"
    x:int=0
    y:int=0
    background_color:Optional[PyGameColor] = None

@dataclass
class CostumeSpec:
    name:str    # name of the costume
    index:int = 0 # index of the image for this costume

@dataclass
class AnimationSpec:
    frame_time_s:float=0.1
    last_frame_time:float=timeit.default_timer()
    loop:bool=True
    started:bool=False


class Actor(pygame.sprite.Sprite):
    def __init__(self, x:int, y:int,
                 enable_transparency:bool=True,
                 angle=0.0,
                 scale_xy:Tuple[float,float]=(1.0, 1.0),
                 physics=common.Physics(enabled=False)):

        super().__init__()

        self.enable_transparency = enable_transparency
        self.angle = angle
        self.scale_xy = scale_xy
        self.animation = AnimationSpec()
        self.physics = physics

        self.costumes:Dict[str, List[pygame.Surface]] = {
            COSTUME_ZERO: [pygame.Surface((0, 0))]
        }

        # initial values
        self.last_shown_costume = CostumeSpec(COSTUME_ZERO, 0)
        self.current_costume = self.last_shown_costume
        self.image = self.get_costume_image(self.current_costume)
        self.rect:pygame.Rect = pygame.Rect(x, y, 0, 0)
        self.mask:Optional[pygame.mask.Mask] = None

        # texts to write
        self.texts:Dict[str, TextInfo] = {}

    def get_costume_image(self, costume:CostumeSpec)->pygame.Surface:
        return self.costumes[costume.name][costume.index]

    def hide(self):
        self.set_costume(COSTUME_ZERO)

    def is_hidden(self)->bool:
        return self.current_costume.name == COSTUME_ZERO

    def show(self):
        self.set_costume(self.last_shown_costume.name, self.last_shown_costume.index)

    def update(self, *args:Any, **kwargs:Any)->None:
        """Update the sprite's position and image."""

        # animate the image if needed
        if self.animation.started:
            if timeit.default_timer() - self.animation.last_frame_time >= self.animation.frame_time_s:
                self.current_costume.index += 1
                if self.current_costume.index >= len(self.costumes[self.current_costume.name]):
                    if self.animation.loop:
                        self.current_costume.index = 0
                    else:
                        self.current_costume.index = len(self.costumes[self.current_costume.name]) - 1
                        self.animation.started = False
                self.animation.last_frame_time = timeit.default_timer()

        # start from current cosume
        self.image = self.get_costume_image(self.current_costume)

        if self.scale_xy != (1.0, 1.0): # scale the image if needed
            self.image = pygame.transform.scale(self.image,
                (int(self.image.get_width() * self.scale_xy[0]),
                    int(self.image.get_height() * self.scale_xy[1])))
        elif len(self.texts) > 0: # if we need to write texts then we need to make copy of the image
            self.image = self.image.copy()
        # else no need to make copy

        for name, text_info in self.texts.items():
            font = pygame.font.Font(text_info.font_name, text_info.font_size)
            surface = font.render(text_info.text, True, text_info.color, text_info.background_color)
            self.image.blit(surface, (text_info.x, text_info.y))

        # rotate the image if needed
        if self.angle != 0.0:
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def glide_to(self, xy:Tuple[float,float], speed:float=1.0)->None:
        """Smoothly move the sprite to a new position."""
        target_vector = pygame.math.Vector2(xy) - pygame.math.Vector2(self.rect.center)
        if target_vector.length() > 0:
            target_vector = target_vector.normalize() * speed
            new_pos = pygame.math.Vector2(self.rect.center) + target_vector
            self.rect.center = new_pos.x, new_pos.y # type: ignore

    def distance_to(self, xy:Tuple[float,float])->float:
        """Return the distance to another sprite."""
        target_vector = pygame.math.Vector2(xy) - pygame.math.Vector2(self.rect.center)
        return target_vector.length()

    def start_animation(self, frame_time_s:float=0.1, loop:bool=True)->None:
        """Cycle through images for current costume"""
        self.animation = AnimationSpec(frame_time_s, timeit.default_timer(), loop, True)

    def stop_animation(self)->None:
        self.animation.started = False

    def add_costume_image(self, name:str,
                          image_path_or_surface:Union[str, Iterable[str], pygame.Surface],
                          transparent_color:Optional[PyGameColor]=None,
                          scale_xy:Optional[Tuple[float,float]]=None,
                          change=False) -> pygame.Surface:

        if isinstance(image_path_or_surface, str):
            image_path_or_surface = [image_path_or_surface] # type: ignore

        surfaces = []
        if isinstance(image_path_or_surface, Iterable):
            for image_path in image_path_or_surface:
                image = common.get_image(image_path)
                surfaces.append(image if image else pygame.Surface((0, 0)))
        elif isinstance(image_path_or_surface, pygame.Surface):
            surfaces.append(image_path_or_surface)
        else:
            raise Exception(f"Invalid image_path_or_surface: {image_path_or_surface}")

        if name not in self.costumes:
            self.costumes[name] = []

        for surface in surfaces:
            # scale the image if needed
            if scale_xy is not None and scale_xy != (1.0, 1.0):
                surface = pygame.transform.scale(surface,
                    (int(surface.get_width() * scale_xy[0]),
                        int(surface.get_height() * scale_xy[1])))

            # set transparency
            if transparent_color is not None:
                surface.set_colorkey(transparent_color)
            else:
                if self.enable_transparency and common.has_transparency(surface):
                    surface = surface.convert_alpha()

            # add to costumes
            self.costumes[name].append(surface)

        if change:
            self.set_costume(name, index=0)

        return surfaces[0]

    def add_costume_rect(self, name:str,
                         width:int=20, height:int=20,
                         color:PyGameColor="red", border=0, change=False) -> pygame.Surface:

        rect:pygame.Rect = pygame.Rect(0, 0, width, height)

        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.rect(surface, color, rect, width=border)

        return self.add_costume_image(name, surface, change=change)

    def add_costume_ellipse(self, name:str,
                       width:int=20, height:int=20,
                    color:PyGameColor="yellow", border=0, change=False) -> pygame.Surface:
        rect:pygame.Rect = pygame.Rect(0, 0, width, height)
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.ellipse(surface, color, rect, width=border)

        return self.add_costume_image(name, surface, change=change)

    def add_text(self, name:str, text:str, font_name:Optional[str]=None,
              font_size:int=20,
              color:PyGameColor="black", x:int=0, y:int=0,
              background_color:Optional[PyGameColor]=None,
              )->None:
        self.texts[name] = TextInfo(text, font_name, font_size, color, x, y, background_color)

    def remove_text(self, name:str)->None:
        if name in self.texts:
            del self.texts[name]

    def append_to_costume(self, name:str, surface:pygame.Surface)->None:
        self.costumes[name].append(surface)

    def save_current_costume(self, name:str)->None:
        """Save current rendering as cosume"""
        self.append_to_costume(name, self.image.copy())

    def add_costume_polygon_any(self, name:str,
                        points:List[Tuple[int, int]],
                        color:PyGameColor="green", border=0, change=False) -> pygame.Surface:
        bounding_rect = common.get_bounding_rect(points)

        # Find the minimum x (left) and y (top) values
        min_x = min(point[0] for point in points)
        min_y = min(point[1] for point in points)

        # Create a new polygon where each point is adjusted by the min_x and min_y
        relative_points = [(x - min_x, y - min_y) for x, y in points]

        surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent color
        pygame.draw.polygon(surface, color, relative_points, width=border)

        return self.add_costume_image(name, surface, change=change)

    def add_costume_polygon(self, name:str,
                    sides:int, width:int=20, height:int=20,
                    color:PyGameColor="green", border=0, change=False) -> pygame.Surface:

        points = common.polygon_points(sides, 0, 0, width, height)
        return self.add_costume_polygon_any(name, points, color, border, change=change)

    def set_costume(self, name:str, index=0)->None:
        if self.current_costume == CostumeSpec(name, index):
            return

        # only record non-hidden costumes
        if self.current_costume.name != COSTUME_ZERO:
            self.last_shown_costume = self.current_costume

        self.current_costume = CostumeSpec(name, index)
        self.image = self.get_costume_image(self.current_costume)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

        # create masks
        if self.image.get_colorkey() is not None:
            self.mask = pygame.mask.from_surface(self.image)
        elif self.enable_transparency and common.has_transparency(self.image):
                self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask:Optional[pygame.mask.Mask] = None

    def remove_costume(self, name:str, index:Optional[int])->None:
        if name in self.costumes:
            if index is None:
                del self.costumes[name]
            else:
                del self.costumes[name][index]

    def move(self, dx:int, dy:int)->pygame.Rect:
        self.rect.move_ip(dx, dy)
        return self.rect

    def turn(self, angle:float)->None:
        """ Rotate a sprite and keep its center. """
        self.angle = angle

    def angle_to(self, xy: Tuple[float, float], speed:float=0.1) -> float:
        # Calculate angle to target
        x_diff = xy[0] - self.rect.centerx
        y_diff = xy[1] - self.rect.centery
        target_angle = math.degrees(math.atan2(-y_diff, x_diff))

        # Adjust the target angle relative to the current angle
        current_angle = self.angle  # Assuming self.angle is maintained elsewhere in your code

        # Calculate the difference in angles and adjust for wrapping
        angle_diff = target_angle - current_angle
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360

        # Smoothly update the angle
        # Here, 'speed' is a factor determining how quickly the angle updates; you can adjust this
        new_angle = current_angle + angle_diff * speed

        return new_angle

    def turn_to(self, xy:Tuple[float,float], speed:float=0.1)->None:
        self.angle = self.angle_to(xy, speed)

    def touches(self, other:Union['Actor', ActorGroup, Tuple[float, float]])->Sequence['Actor']:
        if isinstance(other, Actor):
            if pygame.sprite.collide_mask(self, other):
                return [other]
            else:
                return []
        elif isinstance(other, ActorGroup) or isinstance(other, list):
            return pygame.sprite.spritecollide(self, other, False, collide_mask) # type: ignore
        elif isinstance(other, tuple):
            if self.rect.collidepoint(other):
                return [self]
            else:
                return []

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
