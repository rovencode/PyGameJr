from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable, Callable
import pygame
import pymunk
from pymunk import pygame_util

from pygamejr.common import PyGameColor

class RenderHelper:
    def __init__(self,
                 width:int, height:int,
                 center:Tuple[float, float],
                 draw_shape:Callable[[pygame.Surface, PyGameColor, Tuple[float, float], float], None],
                 color:PyGameColor="green",
                 border=0,
                 border_color:PyGameColor="black",
                 orientation_width=0,
                 orientation_color:PyGameColor="grey",
                 image:Optional[pygame.Surface]=None,
                 image_scale_xy:Tuple[float, float]=(1., 1.),
                 image_transparency_enabled:bool=False,):

        self.width = width
        self.height = height
        self.center = center
        self.color = color
        self.border = border
        self.border_color = border_color
        self.orientation_width = orientation_width
        self.orientation_color = orientation_color
        self.image_orig = self.image = image
        self.image_scale_xy = image_scale_xy
        self.image_transparency_enabled = image_transparency_enabled
        self.draw_shape = draw_shape

        # Resize image to fit the circle
        if self.image is not None:
            if self.image_scale_xy != (1., 1.):
                self.image = pygame.transform.scale(self.image,
                    (int(self.image.get_width() * self.image_scale_xy[0]),
                        int(self.image.get_height() * self.image_scale_xy[1])))

            # crop image outside of the circle
            mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            draw_shape(mask, (255, 255, 255, 255), (0,0), self.border)

            image_topleft = (self.center[0] - self.image.get_width() / 2,
                             self.center[1] - self.image.get_height() / 2)
            mask.blit(self.image, image_topleft,
                      special_flags=pygame.BLEND_RGBA_MULT)
            self.image = mask


    def draw(self, surface, topleft:Tuple[float, float], center:Tuple[float, float], angle:float):
        # Convert body position to pygame coordinates
        center = pygame_util.to_pygame(center, surface)
        topleft = pygame_util.to_pygame(topleft, surface)

        # Draw the circle fill
        if self.image is not None:
            # Blit masked image onto the surface
            surface.blit(self.image, topleft)
        else:
            self.draw_shape(surface, self.color, topleft, self.border)

        # Draw orientation line if enabled
        if self.orientation_width:
            endpoint = pymunk.Vec2d(self.width/2, 0).rotated(angle) + center
            end_pos = pygame_util.to_pygame(endpoint, surface)
            pygame.draw.line(surface, self.orientation_color, center, endpoint, self.orientation_width)
