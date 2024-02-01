from typing import Optional, List, Tuple, Dict, Union, Sequence, Iterable
from collections import namedtuple
from dataclasses import dataclass, field
import math
import os
import timeit
from enum import Enum

import numpy as np

import pygame
import pymunk
from pymunk import pygame_util, Vec2d
from pygamejr import utils

RGBAOutput = Tuple[int, int, int, int]
PyGameColor = Union[pygame.Color, int, str, Tuple[int, int, int], RGBAOutput, Sequence[int]]
_images:Dict[str, pygame.Surface] = {} # cache of all loaded images

NumericNamedTuple = namedtuple('NumericNamedTuple', ['x', 'y'])
NumericNamedTuple.__doc__ = """A named tuple with two numeric fields x and y."""
NumericNamedTuple.__annotations__ = {'x': Union[int, float], 'y': Union[int, float]}

# types that accepts tuples of vectors
Coordinates=Union[Tuple[float, float], Vec2d, NumericNamedTuple]
Vector2=Union[Tuple[float, float], Vec2d, NumericNamedTuple]

def get_image(image_path:str, cache=True)->pygame.Surface:
    """
    Load an image from a file. If the image has already been loaded, return the cached image.
    """
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

def get_bounding_rect(polygon_points:Iterable[Coordinates])->Tuple[float, float, float, float, float, float]:
    """
    Returns a pygame.Rect that contains all of the points in the polygon.
    """

    # Unzip the polygon points into two separate lists of x coordinates and y coordinates
    x_coordinates, y_coordinates = zip(*polygon_points)

    # Use min and max to find the bounding coordinates
    min_x = min(x_coordinates)
    min_y = min(y_coordinates)
    max_x = max(x_coordinates)
    max_y = max(y_coordinates)

    return max_x - min_x, max_y - min_y, min_x, min_y, max_x, max_y

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



class ImagePaintMode(Enum):
    CENTER = 1
    TILE = 2

@dataclass
class TextInfo:
    text:str
    pos:Coordinates=(0, 0)
    font_name:Optional[str]=None
    font_size:int=20
    color:PyGameColor="black"
    background_color:Optional[PyGameColor] = None

@dataclass
class CostumeSpec:
    name:str
    image_paths:Iterable[str]
    scale_xy:Tuple[float,float]=(1., 1.)
    transparent_color:Optional[PyGameColor]=None
    transparency_enabled:bool=False
    images:List[pygame.Surface]=field(default_factory=list)
    paint_mode:ImagePaintMode=ImagePaintMode.CENTER


@dataclass
class CameraControls:
    zoom_in_key='z'
    zoom_out_key='x'
    pan_left_key='a'
    pan_right_key='d'
    pan_up_key='w'
    pan_down_key='s'
    rotate_left_key='q'
    rotate_right_key='e'
    zoom_speed:float=1.1
    pan_speed:float=10.
    rotate_speed:float=5.
    reset_key:str='r'
class Camera:
    def __init__(self) -> None:
        self.bottom_left:Vec2d=Vec2d.zero()
        self.angle:float=0
        self.scale=1.0
        self._update_transform()

    def _update_transform(self):
        if self.angle == 0:
            self.theta = 0
            self.rotation_matrix = np.eye(2)
        else:
            # Convert angle to radians
            self.theta = np.radians(self.angle)
            # Create rotation matrix
            self.rotation_matrix = np.array([[np.cos(self.theta), -np.sin(self.theta)],
                                        [np.sin(self.theta),  np.cos(self.theta)]])
        # Create scaling matrix
        self.scaling_matrix = np.array([[self.scale, 0],
                                [0, self.scale]])

    def apply(self, points:Sequence[Coordinates],
              translate=True, scale=True, rotate=True)->List[Vec2d]:
        points = np.array(points) # type: ignore

        if scale:
            points = np.dot(points, self.scaling_matrix)

        if rotate:
            points = np.dot(points, self.rotation_matrix.T)

        if translate:
            points = points + self.bottom_left # type: ignore

        return [Vec2d(*v) for v in points]

    def move_by(self, delta:Coordinates):
        self.bottom_left += Vec2d(*delta)
        self._update_transform()
    def move_to(self, pos:Coordinates):
        self.bottom_left = Vec2d(*pos)
        self._update_transform()
    def turn_by(self, angle:float):
        self.angle += angle
        self._update_transform()
    def turn_to(self, angle:float):
        self.angle = angle
        self._update_transform()
    def zoom_by(self, scale:float):
        self.scale *= scale
        self._update_transform()
    def zoom_to(self, scale:float):
        self.scale = scale
        self._update_transform()
    def reset(self):
        self.bottom_left = Vec2d.zero()
        self.angle = 0
        self.scale = 1.0
        self._update_transform()

@dataclass
class AnimationSpec:
    frame_time_s:float=0.1
    last_frame_time:float=timeit.default_timer()
    loop:bool=True
    started:bool=False
    image_index:int=0

    def start(self, loop:bool=True, from_index=0, frame_time_s:float=0.1):
        self.started = True
        self.loop = loop
        self.frame_time_s = frame_time_s
        self.image_index = from_index
        self.last_frame_time = timeit.default_timer()

    def stop(self):
        self.started = False

@dataclass
class ImageSpec:
    image:pygame.Surface
    image_scale_xy:Tuple[float,float]=(1., 1.)
    image_transparency_enabled:bool=False

@dataclass
class DrawOptions:
    angle_line_width:int=0
    angle_line_color:PyGameColor="black"
    center_radius:float=0
    center_color:PyGameColor="magenta"

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
                   texts:Dict[str, TextInfo],
                   color:PyGameColor, border:int,
                   draw_options:Optional[DrawOptions],
                   camera:Camera,
                   image:Optional[pygame.Surface]=None,
                   image_paint_mode:ImagePaintMode=ImagePaintMode.CENTER)->Tuple[pygame.Surface, Vec2d]:
    """Creates the surface to fit the given shape and draws on the shape on it.
       Also returns the local coordinates of the center in pygame coordinates.
    """

    surface:Optional[pygame.Surface] = None
    center:Optional[Vec2d] = None

    if isinstance(shape, pymunk.Circle):
        center = Vec2d(shape.radius, shape.radius)
        radius = shape.radius
        angle = shape.body.angle

        # apply transforms
        # No translate because it gets applied by body position later
        center = camera.apply([center], translate=False, rotate=False)[0]
        radius *= camera.scale
        angle += camera.theta

        width, height = int(radius*2), int(radius*2)

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent initial surface
        pygame.draw.circle(surface, color, center, radius, border)

        if draw_options and draw_options.angle_line_width:
            end_pos = (center[0] + int(radius * math.cos(angle)),
                       center[1] - int(radius * math.sin(angle)))
            pygame.draw.line(surface, draw_options.angle_line_color,
                             center, end_pos, round(draw_options.angle_line_width*camera.scale))

    elif isinstance(shape, pymunk.Poly) or isinstance(shape, pymunk.Segment):
        angle = shape.body.angle
        vertices = shape.get_vertices() if isinstance(shape, pymunk.Poly) \
                    else rectangle_from_line(shape.a, shape.b)
        # rotate vertices
        vertices = [v.rotated(shape.body.angle) for v in vertices]

        # apply transforms
        # no translate because it gets applied by body position later
        vertices = camera.apply(vertices, translate=False)
        angle += camera.theta

        min1_x = min([v.x for v in vertices])
        min1_y = min([v.y for v in vertices])
        vertices = [Vec2d(v.x-min1_x, v.y-min1_y) for v in vertices]

        height = max([v.y for v in vertices])
        width = max([v.x for v in vertices])
        # flip y to get pygame coordinates
        vertices = [Vec2d(v.x, height-v.y) for v in vertices]

        # ensure, min x and y is 0 by translating all vertices by min x and y
        min2_y = min([v.y for v in vertices])
        vertices = [Vec2d(v.x, v.y-min2_y) for v in vertices]

        # create surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0)) # transparent initial surface
        pygame.draw.polygon(surface, color, vertices, border)

        # body coordinates translates in the same way as the vertices
        # get_vertices() assumes body at (0, 0) and we translate it to (min1_x, min1_y)
        center = Vec2d(0-min1_x, height-(0-min1_y)-min2_y)

        if draw_options and draw_options.angle_line_width:
            unit_vector = Vec2d(1, 0).rotated(angle) # add 180 degree to flip y
            angle_vec = center + (unit_vector * (width + height) / 2.0)
            pygame.draw.line(surface, color, center, angle_vec, border)
    else:
        raise ValueError(f"Unknown shape type: {type(shape)}")

    # crop image outside of the shape
    if image is not None:
        # image without transformations
        angle = shape.body.angle
        if angle != 0:
            image = pygame.transform.rotate(image, math.degrees(angle))

        image_rect = [(0, 0), (image.get_width(), 0),
                      (image.get_width(), image.get_height()), (0, image.get_height())]


        # apply scale and rotation
        if camera.scale != 1.0:
            image = pygame.transform.scale(image, (int(image.get_width()*camera.scale),
                                                   int(image.get_height()*camera.scale)))
        if camera.theta != 0:
            image = pygame.transform.rotate(image, math.degrees(camera.theta))

        if image_paint_mode == ImagePaintMode.CENTER:
            image_rect = camera.apply(image_rect, translate=False)
            max_x, min_x = max([v.x for v in image_rect]), min([v.x for v in image_rect])
            max_y, min_y = max([v.y for v in image_rect]), min([v.y for v in image_rect])
            width, height = max_x - min_x, max_y - min_y
            # recenter image on the shape
            image_offset = center - Vec2d(width, height)/2.

            surface.blit(image, image_offset)
        else:
            # Get the size of the texture image
            texture_width, texture_height = image.get_size()
            surface_width, surface_height = surface.get_size()
            # Tile the image across the screen
            for x in range(0, surface_width, texture_width):
                for y in range(0, surface_height, texture_height):
                    surface.blit(image, (x, y))

    if draw_options and draw_options.center_radius:
        pygame.draw.circle(surface, draw_options.center_color,
                           center, draw_options.center_radius, 0)

    draw_texts(surface, texts)

    return surface, center

def draw_texts(surface:pygame.Surface, texts:Dict[str, TextInfo]):
    for name, text_info in texts.items():
        font = pygame.font.Font(text_info.font_name, text_info.font_size)
        text_surface = font.render(text_info.text, True, text_info.color, text_info.background_color)
        pos = tuple(text_info.pos)
        surface.blit(text_surface, pos)

def print_to(surface:pygame.Surface, text:str, topleft:Coordinates=Vec2d.zero(),
             font_name:Optional[str]=None, font_size:int=20,
             color:PyGameColor="black", background_color:Optional[PyGameColor]=None):
    """Prints the given text to the given surface at the given position."""
    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(text, True, color, background_color)
    surface.blit(text_surface, topleft)

def tiled_blit(source:pygame.Surface, start_xy:Tuple[int, int], dest:pygame.Surface):
    start_x, start_y = start_xy
    source_width, source_height = source.get_width(), source.get_height()
    dest_width, dest_height = dest.get_width(), dest.get_height()

    # Adjust start_x and start_y for negative values to ensure tiling works correctly
    if start_x < 0:
        start_x = source_width - (-start_x % source_width)
    if start_y < 0:
        start_y = source_height - (-start_y % source_height)

    # Calculate the starting points for tiling considering negative offsets
    start_x = start_x % source_width - source_width
    start_y = start_y % source_height - source_height

    # Tile the source across the dest
    for x in range(start_x, dest_width, source_width):
        for y in range(start_y, dest_height, source_height):
            dest.blit(source, (x, y))