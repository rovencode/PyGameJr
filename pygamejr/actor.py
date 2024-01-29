from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable, Callable, Sequence
import math
import timeit

import pygame
import pymunk
from pymunk import pygame_util, Vec2d

from pygamejr.common import PyGameColor, AnimationSpec, TextInfo,  \
                            surface_from_shape, CostumeSpec, Coordinates, \
                            DrawOptions
from pygamejr import common


class Actor:
    def __init__(self,
                 shape:pymunk.Shape,
                 color:PyGameColor="green",
                 border=0,
                 image_paths:Optional[Union[str, Iterable[str]]]=None,
                 image_scale_xy:Tuple[float, float]=(1., 1.),
                 image_transparent_color:Optional[PyGameColor]=None,
                 image_transparency_enabled:bool=False,
                 image_shape_crop:bool=False,
                 visible:bool=True,
                 draw_options:Optional[DrawOptions]=None):

        self.shape = shape
        self.color = color
        self.border = border
        self.draw_options = draw_options
        self.visible = visible

        self.animation = AnimationSpec()
        self.texts:Dict[str, TextInfo] = {}
        self.current_image:Optional[pygame.Surface] = None

        self.costumes:Dict[str, CostumeSpec] = {}
        self.current_costume:Optional[CostumeSpec] = None

        if image_paths:
            self.add_costume("", image_paths=image_paths,
                            scale_xy=image_scale_xy,
                            transparent_color=image_transparent_color,
                            transparency_enabled=image_transparency_enabled,
                            shape_crop=image_shape_crop, change=True)

    def start_animation(self, loop:bool=True, from_index=0, frame_time_s:float=0.1):
        self.animation.start(loop, from_index, frame_time_s)
    def stop_animation(self):
        self.animation.stop()
    def show(self):
        self.visible = True
    def hide(self):
        self.visible = False

    def add_costume(self, name:str, image_paths:Union[str, Iterable[str]],
                    scale_xy:Tuple[float, float]=(1., 1.),
                    transparent_color:Optional[PyGameColor]=None,
                    transparency_enabled:bool=False,
                    shape_crop:bool=False,
                    change:bool=False):

        if isinstance(image_paths, str):
            image_paths = [image_paths] # type: ignore

        costume = CostumeSpec(name, image_paths,
                        scale_xy=scale_xy,
                        transparent_color=transparent_color,
                        transparency_enabled=transparency_enabled,
                        shape_crop=shape_crop)
        self.costumes[name] = costume

        for image_path in image_paths:
            # load image
            image = common.get_image(image_path)
            # set transparency
            if costume.transparent_color is not None:
                image.set_colorkey(costume.transparent_color)
            else:
                if costume.transparency_enabled and common.has_transparency(image):
                        image = image.convert_alpha()
            costume.images.append(image)

        if change:
            self.current_costume = costume

    def add_text(self, name:str, text:str, font_name:Optional[str]=None,
              font_size:int=20,
              color:PyGameColor="black", x:int=0, y:int=0,
              background_color:Optional[PyGameColor]=None,
              )->None:
        self.texts[name] = TextInfo(text, font_name, font_size, color, x, y, background_color)

    def remove_text(self, name:str)->None:
        if name in self.texts:
            del self.texts[name]

    def set_cosume(self, name:Optional[str])->None:
        if name is None:
            self.current_costume = None
        else:
            self.current_costume = self.costumes[name]

    def glide_to(self, xy:Coordinates, speed:float=1.0)->None:
        """Smoothly move the body to a new position."""
        target_vector = Vec2d(*xy) - self.shape.body.position
        if target_vector.length() > 0:
            target_vector = target_vector.normalize() * speed
            self.shape.body.position = self.shape.body.position + target_vector

    def move_by(self, xy:Coordinates)->None:
        """Move the body by a vector."""
        self.shape.body.position = self.shape.body.position + Vec2d(*xy)
    def move_to(self, xy:Coordinates)->None:
        """Move the body to a new position."""
        self.shape.body.position = Vec2d(*xy)

    def turn_by(self, angle:float)->None:
        """Turn the body by an angle."""
        self.shape.body.angle += math.radians(angle)

    def turn_to(self, angle:float)->None:
        """Turn the body to an angle."""
        self.shape.body.angle = math.radians(angle)

    def turn_towards(self, xy:Coordinates)->None:
        """Turn the body towards a point."""
        target_vector = Vec2d(*xy) - self.shape.body.position
        self.shape.body.angle = target_vector.angle

    def touches(self, other:Optional[Union['Actor', List['Actor']]])->Union[List['Actor'], List[pymunk.ShapeQueryInfo]]:
        if self.shape.space is None:
            return []

        colliding_shapes = self.shape.space.shape_query(self.shape)

        if other  is None:
            other = []
        elif not isinstance(other, list):
            other = [other]

        if len(other) == 0:
            return colliding_shapes
        else:
            other_shapes = {o.shape:o for o in other}
            return [other_shapes[s] for s in colliding_shapes if s in other_shapes]

    def distance_to(self, xy:Coordinates)->float:
        """Return the distance to another sprite."""
        target_vector = Vec2d(*xy) - self.shape.body.position
        return target_vector.length()

    def x(self)->float:
        return self.shape.body.position.x
    def y(self)->float:
        return self.shape.body.position.y
    def center(self)->Tuple[float, float]:
        return self.x(), self.y()
    def width(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.right - self.shape.bb.left
    def height(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.top - self.shape.bb.bottom
    def topleft(self)->Tuple[float, float]:
        self.shape.cache_bb()
        return self.shape.bb.left, self.shape.bb.top
    def topright(self)->Tuple[float, float]:
        self.shape.cache_bb()
        return self.shape.bb.right, self.shape.bb.top
    def bottomleft(self)->Tuple[float, float]:
        self.shape.cache_bb()
        return self.shape.bb.left, self.shape.bb.bottom
    def bottomright(self)->Tuple[float, float]:
        self.shape.cache_bb()
        return self.shape.bb.right, self.shape.bb.bottom
    def top(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.top
    def bottom(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.bottom
    def left(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.left
    def right(self)->float:
        self.shape.cache_bb()
        return self.shape.bb.right
    def rect(self)->Tuple[float, float, float, float]:
        self.shape.cache_bb()
        return (self.shape.bb.left, self.shape.bb.top, self.width(), self.height())
    def is_hidden(self)->bool:
        return not self.visible


    def remove_costume(self, name:str)->None:
        if name in self.costumes:
            del self.costumes[name]
            if self.current_costume is not None and self.current_costume.name == name:
                self.set_cosume(None)

    def update(self)->None:
        if self.current_costume is not None:
            if self.animation.started:
                if timeit.default_timer() - self.animation.last_frame_time >= self.animation.frame_time_s:
                    self.animation.image_index += 1
                    self.animation.last_frame_time = timeit.default_timer()
                    if self.animation.image_index >= len(self.current_costume.images):
                        if self.animation.loop:
                            self.animation.image_index = 0
                        else:
                            self.animation.image_index = len(self.current_costume.images)-1
                            self.animation.stop()
            self.current_image = self.current_costume.images[self.animation.image_index]
            # scale image
            if self.current_costume.scale_xy != (1., 1.):
                image = pygame.transform.scale(self.current_image,
                    (int(self.current_image.get_width() * self.current_costume.scale_xy[0]),
                        int(self.current_image.get_height() * self.current_costume.scale_xy[1])))
            elif len(self.texts) > 0: # if we need to write texts then we need to make copy of the image
                self.current_image = self.current_image.copy()
            # else no need to make copy

            for name, text_info in self.texts.items():
                font = pygame.font.Font(text_info.font_name, text_info.font_size)
                surface = font.render(text_info.text, True, text_info.color, text_info.background_color)
                self.current_image.blit(surface, (text_info.x, text_info.y))

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

    def draw(self, screen:pygame.Surface):
        if self.visible:
            surface, center = surface_from_shape(shape=self.shape,
                                         color=self.color,
                                         border=self.border,
                                         draw_options=self.draw_options,
                                         image=self.current_image,
                                         image_shape_crop=self.current_costume.shape_crop \
                                             if self.current_costume else True)
            pos = Vec2d(*pygame_util.to_pygame(self.shape.body.position, screen))
            screen.blit(surface, pos-center)
