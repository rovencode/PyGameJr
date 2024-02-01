from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable, Callable, Sequence, Sized
import math
import timeit

import pygame
import pymunk
from pymunk import pygame_util, Vec2d

from pygamejr.common import PyGameColor, AnimationSpec, TextInfo,  \
                            surface_from_shape, CostumeSpec, Coordinates, \
                            DrawOptions, ImagePaintMode
from pygamejr import common


class Actor:
    def __init__(self,
                 shape:pymunk.Shape,
                 color:PyGameColor="green",
                 border=0,
                 image_paths:Optional[Union[str, Iterable[str]]]=None,
                 image_scale_xy:Tuple[float,float]=(1., 1.),
                 image_transparent_color:Optional[PyGameColor]=None,
                 image_transparency_enabled:bool=True,
                 image_paint_mode:ImagePaintMode=ImagePaintMode.CENTER,
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
                            paint_mode=image_paint_mode,
                            change=True)

    def start_animation(self, loop:bool=True, from_index=0, frame_time_s:float=0.1):
        self.animation.start(loop, from_index, frame_time_s)
    def stop_animation(self):
        self.animation.stop()
    def show(self):
        self.visible = True
    def hide(self):
        self.visible = False

    @property
    def velocity(self)->Vec2d:
        return self.shape.body.velocity
    @velocity.setter
    def velocity(self, value:Vec2d):
        self.shape.body.velocity = value
    @property
    def position(self)->Vec2d:
        return self.shape.body.position
    @position.setter
    def position(self, value:Vec2d):
        self.shape.body.position = value
    @property
    def angle(self)->float:
        return math.degrees(self.shape.body.angle)
    @angle.setter
    def angle(self, value:float):
        self.shape.body.angle = math.radians(value)
    @property
    def angular_velocity(self)->float:
        return math.degrees(self.shape.body.angular_velocity)
    @angular_velocity.setter
    def angular_velocity(self, value:float):
        self.shape.body.angular_velocity = math.radians(value)
    @property
    def mass(self)->float:
        return self.shape.body.mass
    @mass.setter
    def mass(self, value:float):
        self.shape.body.mass = value
    @property
    def moment(self)->float:
        return self.shape.body.moment
    @moment.setter
    def moment(self, value:float):
        self.shape.body.moment = value
    @property
    def friction(self)->float:
        return self.shape.friction
    @friction.setter
    def friction(self, value:float):
        self.shape.friction = value
    @property
    def elasticity(self)->float:
        return self.shape.elasticity
    @elasticity.setter
    def elasticity(self, value:float):
        self.shape.elasticity = value
    @property
    def collision_type(self)->int:
        return self.shape.collision_type
    @collision_type.setter
    def collision_type(self, value:int):
        self.shape.collision_type = value
    @property
    def group(self)->int:
        return self.shape.group
    @group.setter
    def group(self, value:int):
        self.shape.group = value

    def apply_force(self, force:Coordinates, local_point:Coordinates=(0,0))->None:
        self.shape.body.apply_force_at_local_point(force, local_point)
    def apply_impulse(self, impulse:Coordinates, local_point:Coordinates=(0,0))->None:
        self.shape.body.apply_impulse_at_local_point(impulse, local_point)
    def apply_torque(self, torque:float)->None:
        self.shape.body.apply_torque(torque)
    def apply_local_force(self, force:Coordinates, local_point:Coordinates=(0,0))->None:
        self.shape.body.apply_force_at_local_point(force, local_point)
    def apply_local_impulse(self, impulse:Coordinates, local_point:Coordinates=(0,0))->None:
        self.shape.body.apply_impulse_at_local_point(impulse, local_point)
    def apply_impulse_torque(self, impulse_torque):
        """
        Apply an impulse torque to a PyMunk body.

        :param body: The PyMunk body to which the impulse torque is applied.
        :param impulse_torque: The amount of impulse torque to apply.
        """
        # Angular impulse is change in angular momentum, which is I * Δω
        # Δω (change in angular velocity) = impulse_torque / moment_of_inertia
        if self.shape.body.moment.iszero():
            return
        angular_velocity_change = impulse_torque / self.shape.body.moment
        self.shape.body.angular_velocity += angular_velocity_change

    def add_costume(self, name:str, image_paths:Union[str, Iterable[str]],
                    scale_xy:Tuple[float,float]=(1., 1.),
                    transparent_color:Optional[PyGameColor]=None,
                    transparency_enabled:bool=False,
                    paint_mode:ImagePaintMode=ImagePaintMode.CENTER,
                    change:bool=False):

        if isinstance(image_paths, str):
            image_paths = [image_paths] # type: ignore

        costume = CostumeSpec(name, image_paths,
                        scale_xy=scale_xy,
                        transparent_color=transparent_color,
                        transparency_enabled=transparency_enabled,
                        paint_mode=paint_mode)
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

    def add_text(self, text:str, font_name:Optional[str]=None,
              font_size:int=20,
              color:PyGameColor="black", x:int=0, y:int=0,
              background_color:Optional[PyGameColor]=None,
              name:Optional[str]=None)->None:
        if name is None:
            name = text
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
        if target_vector.length > 0:
            target_vector = target_vector.normalized() * speed
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

    def touches_at(self, point:Coordinates)->bool:
        query_result = self.shape.point_query(point)
        return query_result.distance <= 0


    def touches(self, other:Optional[Union['Actor', Sequence['Actor']]])->Union[List['Actor'], List[pymunk.ShapeQueryInfo]]:
        if self.shape.space is None:
            return []

        colliding_shapes = self.shape.space.shape_query(self.shape)

        if other  is None:
            other = []
        elif not isinstance(other, Sequence):
            other = [other]

        if len(other) == 0:
            return colliding_shapes
        else:
            other_shapes = {o.shape:o for o in other}
            return [other_shapes[s.shape] for s in colliding_shapes if s.shape in other_shapes]

    def distance_to(self, xy:Coordinates)->float:
        """Return the distance to another sprite."""
        target_vector = Vec2d(*xy) - self.shape.body.position
        return target_vector.length

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
                self.current_image = pygame.transform.scale(
                    self.current_image,(
                        self.current_image.get_width()*self.current_costume.scale_xy[0], \
                        self.current_image.get_height()*self.current_costume.scale_xy[1]
                    ))
            else:
                self.current_image = self.current_image.copy()

    def _recreate_shape(self, new_width, new_height)->None:
        self.shape.cache_bb()
        width, height = self.width(), self.height()
        body, space, offset = self.shape.body, self.shape.space, self.shape.offset
        assert space is not None
        space.remove(self.shape)
        if isinstance(self.shape, pymunk.Circle):
            self.shape = pymunk.Circle(body, max(new_width, new_height)/2., offset)
        elif isinstance(self.shape, pymunk.Poly):
            vertices, radius = self.shape.get_vertices(), self.shape.radius
            x_scale, y_scale = new_width/width, new_height/height
            vertices = [(v.x*x_scale, v.y*y_scale) for v in vertices]
            self.shape = pymunk.Poly(body, vertices, radius=radius)
        elif isinstance(self.shape, pymunk.Segment):
            a, b, radius = self.shape.a, self.shape.b, self.shape.radius
            a = (a.x*new_width/width, a.y*new_height/height)
            b = (b.x*new_width/width, b.y*new_height/height)
            self.shape = pymunk.Segment(body, a, b, radius)
        else:
            raise ValueError(f"Unknown shape type {self.shape}")
        space.add(self.shape)


    def fit_to_image(self)->None:
        if self.current_costume is not None and len(self.current_costume.images):
            new_width, new_height = self.current_costume.images[0].get_size()
            if isinstance(self.shape, pymunk.Circle):
                self.shape.unsafe_set_radius(max(new_width, new_height)/2.)
            elif isinstance(self.shape, pymunk.Poly):
                vertices = self.shape.get_vertices()
                x_scale, y_scale = new_width/self.width(), new_height/self.height()
                vertices = [(v.x*x_scale, v.y*y_scale) for v in vertices]
                self.shape.unsafe_set_vertices(vertices)
            elif isinstance(self.shape, pymunk.Segment):
                a, b = self.shape.a, self.shape.b
                a = (a.x*new_width/self.width(), a.y*new_height/self.height())
                b = (b.x*new_width/self.width(), b.y*new_height/self.height())
                self.shape.unsafe_set_endpoints(a, b)

    def fit_image(self)->None:
        if self.current_costume is not None and len(self.current_costume.images):
            new_width, new_height = self.width(), self.height()
            old_width, old_height = self.current_costume.images[0].get_size()
            if new_width != old_width or new_height != old_height:
                self.current_costume.scale_xy = (new_width/old_width, new_height/old_height)

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
                                         texts=self.texts,
                                         color=self.color,
                                         border=self.border,
                                         draw_options=self.draw_options,
                                         image=self.current_image,
                                         image_paint_mode=self.current_costume.paint_mode \
                                            if self.current_costume else ImagePaintMode.CENTER ,)
            pos = Vec2d(*pygame_util.to_pygame(self.shape.body.position, screen))
            screen.blit(surface, pos-center)
