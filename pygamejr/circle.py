from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable
import pygame
import pymunk
from pymunk import pygame_util

from pygamejr.common import PyGameColor

class Circle(pymunk.Circle):
    def __init__(self, body:pymunk.Body, radius:float,
                 offset=(0, 0), border=0,
                 color:PyGameColor="green",
                 border_color:PyGameColor="black",
                 orientation_width=0,
                 orientation_color:PyGameColor="grey",
                 image:Optional[pygame.Surface]=None,
                 image_scale_xy:Tuple[float, float]=(1., 1.),
                 image_transparency_enabled:bool=False,):

        super().__init__(body, radius, offset)
        self.color = color
        self.border = border
        self.border_color = border_color
        self.orientation_width = orientation_width
        self.orientation_color = orientation_color
        self.image_orig = self.image = image
        self.image_scale_xy = image_scale_xy
        self.image_transparency_enabled = image_transparency_enabled

        # Resize image to fit the circle
        if self.image is not None:
            if self.image_scale_xy != (1., 1.):
                self.image = pygame.transform.scale(self.image,
                    (int(self.image.get_width() * self.image_scale_xy[0]),
                        int(self.image.get_height() * self.image_scale_xy[1])))

            if (self.image.get_width() > 2 * (self.radius - self.border) or \
                self.image.get_height() > 2 * (self.radius - self.border)):
                    self.image = pygame.transform.scale(self.image,
                        (2 * (self.radius - self.border),
                        2 * (self.radius - self.border)))

            # crop image outside of the circle
            mask = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
            # Create a mask to make areas outside the circle transparent
            pygame.draw.circle(surface=mask, color=(255, 255, 255, 255),
                               center=(self.radius, self.radius),
                               radius=self.radius - self.border)

            mask.blit(self.image, (self.border, self.border), None, pygame.BLEND_RGBA_MULT)
            self.image = mask


    def draw(self, surface):
        # Convert body position to pygame coordinates
        pos = pygame_util.to_pygame(self.body.position, surface)

        # Draw the circle border
        if self.border > 0:
            pygame.draw.circle(surface, self.border_color, pos, self.radius)

        # Draw the circle fill
        if self.image is not None:
            # Blit masked image onto the surface
            surface.blit(self.image, (pos[0] - self.radius, pos[1] - self.radius))
        else:
            pygame.draw.circle(surface, self.color, pos, self.radius, self.border)

        # Draw orientation line if enabled
        if self.orientation_width:
            endpoint = pymunk.Vec2d(self.radius, 0).rotated(self.body.angle) + self.body.position
            end_pos = pygame_util.to_pygame(endpoint, surface)
            pygame.draw.line(surface, self.orientation_color, pos, end_pos, self.orientation_width)
