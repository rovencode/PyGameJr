from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable, Callable
import math

import pygame
import pymunk
from pymunk import pygame_util, Vec2d

from pygamejr.common import PyGameColor, AnimationSpec, TextInfo
from pygamejr import common

class Shape:
    def __init__(self,
                 shape:pymunk.Shape,
                 color:PyGameColor="green",
                 border=0,
                 border_color:PyGameColor="black",
                 orientation_width=0,
                 orientation_color:PyGameColor="grey",
                 image_paths:Optional[Union[str, List[str]]]=None,
                 image_scale_xy:Tuple[float, float]=(1., 1.),
                 image_transparent_color:Optional[PyGameColor]=None,
                 image_transparency_enabled:bool=False,
                 image_shape_crop_enabled:bool=False):

        self.shape = shape
        self.color = color
        self.border = border
        self.border_color = border_color
        self.orientation_width = orientation_width
        self.orientation_color = orientation_color
        self.image_paths = image_paths
        self.image_scale_xy = image_scale_xy
        self.image_transparency_enabled = image_transparency_enabled
        self.image_shape_crop_enabled = image_shape_crop_enabled

        bb = self.shape.cache_bb()
        self.width = bb.right - bb.left
        self.height = bb.top - bb.bottom
        self.center = (self.width/2, self.height/2)

        self.images = []
        self.animation = AnimationSpec()
        self.texts:Dict[str, TextInfo] = {}

        # if image paths are provided,
        if self.image_paths is not None:
            if isinstance(self.image_paths, str):
                self.image_paths = [self.image_paths] # type: ignore

            for image_path in self.image_paths:
                # load image
                image = common.get_image(image_path)
                image = image if image else pygame.Surface((0, 0))
                # scale image
                if self.image_scale_xy != (1., 1.):
                    image = pygame.transform.scale(image,
                        (int(image.get_width() * image_scale_xy[0]),
                            int(image.get_height() * image_scale_xy[1])))
                # crop image to shape
                if self.image_shape_crop_enabled:
                    # crop image outside of the shape
                    mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

                    draw_shape_fn(mask, (255, 255, 255, 255), (0,0), self.border)

                    image_topleft = (self.center[0] - self.image.get_width() / 2,
                                    self.center[1] - self.image.get_height() / 2)
                    mask.blit(self.image, image_topleft,
                            special_flags=pygame.BLEND_RGBA_MULT)
                    self.image = mask
                # set transparency
                if image_transparent_color is not None:
                    image.set_colorkey(image_transparent_color)
                else:
                    if self.image_transparency_enabled and \
                        common.has_transparency(image):
                            image = image.convert_alpha()
                self.images.append(image)

    def draw_polygon_primitive(self, surface:pygame.Surface,
                               color:PyGameColor, border=0):
        p = self.shape.body.position
        p = pygame_util.to_pygame(p, surface)

        # we need to rotate 180 degrees because of the y coordinate flip
        angle_degrees = math.degrees(self.shape.body.angle) + 180
        rotated_logo_img = pygame.transform.rotate(logo_img, angle_degrees)

        offset = Vec2d(*rotated_logo_img.get_size()) / 2
        p = p - offset

        surface.blit(rotated_logo_img, (round(p.x), round(p.y)))

        # debug draw
        ps = [
            p.rotated(self.shape.body.angle) + self.shape.body.position
            for p in self.shape.get_vertices()
        ]
        ps = [pygame_util.to_pygame(p, surface) for p in ps]
        ps += [ps[0]]
        pygame.draw.lines(surface, color, False, ps, border)


    def draw_primitive(self, surface:pygame.Surface, color:PyGameColor,
                       topleft:Tuple[float, float], border:int):
        if isinstance(self.shape, pymunk.Circle):
            pygame.draw.circle(surface, color, topleft, self.shape.radius, border)
        elif isinstance(self.shape, pymunk.Segment):
            pygame.draw.line(surface, color, topleft, self.shape.a, border)
        elif isinstance(self.shape, pymunk.Poly):
            pygame.draw.polygon(surface, color, topleft, border)
        else:
            raise ValueError(f"Unknown shape type: {type(self.shape)}")

    def draw(self, surface, topleft:Tuple[float, float], center:Tuple[float, float], angle:float):
        # Convert body position to pygame coordinates
        center = pygame_util.to_pygame(center, surface)
        topleft = pygame_util.to_pygame(topleft, surface)

        # Draw the circle fill
        if self.image is not None:
            # Blit masked image onto the surface
            surface.blit(self.image, topleft)
        else:
            self.draw_shape_fn(surface, self.color, topleft, self.border)

        # Draw orientation line if enabled
        if self.orientation_width:
            endpoint = pymunk.Vec2d(self.width/2, 0).rotated(angle) + center
            end_pos = pygame_util.to_pygame(endpoint, surface)
            pygame.draw.line(surface, self.orientation_color, center, endpoint, self.orientation_width)


