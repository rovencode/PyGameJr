from typing import Optional, List, Tuple, Dict, Union, Sequence
from collections import namedtuple
from dataclasses import dataclass, field
import math
import os
import timeit

import numpy as np

import pygame
import pymunk
from pymunk import pygame_util, Vec2d
from pygamejr import utils

RGBAOutput = Tuple[int, int, int, int]
PyGameColor = Union[pygame.Color, int, str, Tuple[int, int, int], RGBAOutput, Sequence[int]]
_images:Dict[str, pygame.Surface] = {} # cache of all loaded images

def get_image(image_path:Optional[str], cache=True)->Optional[pygame.Surface]:
    """
    Load an image from a file. If the image has already been loaded, return the cached image.
    """
    if image_path is None:
        return None
    if image_path not in _images:
        image = pygame.image.load(utils.full_path_abs(image_path))
        if cache:
            _images[image_path] = image
    else:
        image = _images[image_path]
    return image

def polygon_points(sides:int, left:int, top:int, polygon_width:int, polygon_height:int)->List[Tuple[int, int]]:
    """
    Computes the coordinates of the points of a regular polygon.
    """

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
    """
    Returns a pygame.Rect that contains all of the points in the polygon.
    """

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

def has_transparency(surface:pygame.Surface)->bool:
    """
    Returns True if the surface has transparency, False otherwise.
    """
    if surface.get_flags() & pygame.SRCALPHA:
        # Surface is per pixel alpha
        mask = pygame.mask.from_surface(surface)
        return mask.count() < mask.get_rect().width * mask.get_rect().height
    elif surface.get_colorkey() is not None:
        # Surface is color key alpha
        return True
    else:
        # No transparency
        return False

def collide_mask_ex(left:pygame.sprite.Sprite, right:pygame.sprite.Sprite)->bool:
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


@dataclass
class Physics:
    enabled:bool = False
    velocity:pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)
    force:pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)
    mass:float = 1.0
    fixed:bool = False # can this object move (for example walls are fixed)?
    infinite_wall:bool = False # is this an infinite wall which may not have center (for example the bottom wall)?

    def __post_init__(self):
        # if fixed object, then mass is infinite
        if self.fixed:
            self.mass = 1.0E9 # some high number to represent infinity

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

@dataclass
class ImageSpec:
    image:pygame.Surface
    image_scale_xy:Tuple[float, float]=(1., 1.)
    image_transparency_enabled:bool=False

def rectangle_from_line(p1:Vec2d, p2:Vec2d)->Tuple[Vec2d, Vec2d, Vec2d, Vec2d]:
    """Create a rectangle around a line of width 1."""
    # Calculate the vector representing the line
    line_vec = p2 - p1

    # Calculate a perpendicular vector (for width)
    perp_vec = Vec2d(-line_vec[1], line_vec[0])

    # Normalize and scale the perpendicular vector to half the rectangle's width
    perp_vec = perp_vec / perp_vec.length * 0.5

    # Calculate the four corners of the rectangle
    corner1 = p1 + perp_vec
    corner4 = p2 + perp_vec
    corner3 = p2 - perp_vec
    corner2 = p1 - perp_vec

    return corner1, corner2, corner3, corner4

def surface_from_shape(shape:pymunk.Shape,
                   color:PyGameColor, border:int,
                   angle_line_width:int, angle_line_color:PyGameColor,
                   center_radius:float, center_color:PyGameColor)->Tuple[pygame.Surface, Vec2d]:
    """Creates the surface to fit the given shape and draws on the shape on it.
       Also returns the local coordinates of the center in pygame coordinates.
    """

    surface:Optional[pygame.Surface] = None
    center:Optional[Vec2d] = None
    if isinstance(shape, pymunk.Circle):
        width, height = shape.radius*2, shape.radius*2
        center = Vec2d(shape.radius, shape.radius)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent initial surface
        pygame.draw.circle(surface, color, center, shape.radius, border)

        if angle_line_width:
            angle = math.degrees(shape.body.angle) + 180 # flipped y
            end_pos = (center[0] + int(shape.radius * math.cos(angle)),
                       center[1] - int(shape.radius * math.sin(angle)))
            pygame.draw.line(surface, angle_line_color, center, end_pos, angle_line_width)

    elif isinstance(shape, pymunk.Poly) or isinstance(shape, pymunk.Segment):
        vertices = shape.get_vertices() if isinstance(shape, pymunk.Poly) \
                    else rectangle_from_line(shape.a, shape.b)
        # rotate vertices
        vertices = [v.rotated(shape.body.angle) for v in vertices]
        height = max([v.y for v in vertices]) - min([v.y for v in vertices])
        # flip y to get pygame coordinates
        vertices = [Vec2d(v.x, height-v.y) for v in vertices]

        # ensure, min x and y is 0 by translating all vertices by min x and y
        min_x = min([v.x for v in vertices])
        min_y = min([v.y for v in vertices])
        vertices = [Vec2d(v.x-min_x, v.y-min_y) for v in vertices]

        # create surface
        width = max([v.x for v in vertices])
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent initial surface
        pygame.draw.polygon(surface, color, vertices, border)

        # body coordinates translates in the same way as the vertices
        center = Vec2d(shape.body.position.x-min_x, (height-shape.body.position.y)-min_y)

        if angle_line_width:
            unit_vector = Vec2d(1, 0).rotated(shape.body.angle + math.pi) # add 180 degree to flip y
            angle_vec = center + (unit_vector * (width + height) / 2.0)
            pygame.draw.line(surface, color, center, angle_vec, border)
    else:
        raise ValueError(f"Unknown shape type: {type(shape)}")

    if center_radius:
        pygame.draw.circle(surface, center_color, center, center_radius, 0)
