from typing import Optional, List, Tuple
import math
import os
import pygame
from pygamejr import utils

_images = {} # cache of all loaded images

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
