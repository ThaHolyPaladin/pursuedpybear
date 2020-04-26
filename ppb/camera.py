"""
:class:`Cameras <Camera>` are objects that straddle the line between game space
and screen space. The renderer uses the position of the camera to translate
:class:`Sprite's <ppb.Sprite>` positions to the screen in order to make them
visible.

The :class:`~ppb.systems.Renderer` inserts a :class:`Camera` into the current
scene in response to the :class:`~ppb.events.SceneStarted`.
"""
from typing import Tuple
from numbers import Real

from ppb_vector import Vector


class Camera:
    """
    A simple Camera.

    Intentionally tightly coupled to the renderer to allow information flow
    back and forth.

    There is a one-to-one relationship between cameras and scenes.

    You can subclass Camera to add event handlers. If you do so, set the
    camera_class class attribute of your scene to your subclass. The renderer
    will instantiate the correct type.
    """
    position = Vector(0, 0)
    size = 0  # Cameras never render, so their logical game unit size is 0

    def __init__(self, renderer, target_game_unit_width: Real,
                 viewport_dimensions: Tuple[int, int]):
        """
        You shouldn't instantiate your own camera in general. If you want to
        override the Camera, see above.

        :param renderer: The renderer associated with the camera.
        :type renderer: ~ppb.systems.renderer.Renderer
        :param target_game_unit_width: The number of game units wide you
           would like to display. The actual width may be less than this
           depending on the ratio to the viewport (as it can only be as wide
           as there are pixels.)
        :type target_game_unit_width: Real
        :param viewport_dimensions: The pixel dimensions of the rendered
           viewport in (width, height) form.
        :type viewport_dimensions: Tuple[int, int]
        """
        self.renderer = renderer
        self.target_game_unit_width = target_game_unit_width
        self.viewport_dimensions = viewport_dimensions
        self.pixel_ratio = None
        self._width = None
        self._height = None
        self._set_dimensions(target_width=target_game_unit_width)

    @property
    def width(self) -> Real:
        """
        The game unit width of the viewport.

        See :mod:`ppb.sprites` for details about game units.

        When setting this property, the resulting width may be slightly
        different from the value provided based on the ratio between the width
        of the window in screen pixels and desired number of game units to
        represent.

        When you set the width, the height will change as well.
        """
        return self._width

    @width.setter
    def width(self, target_width):
        self._set_dimensions(target_width=target_width)

    @property
    def height(self) -> Real:
        """
        The game unit height of the viewport.

        See :mod:`ppb.sprites` for details about game units.

        When setting this property, the resulting height may be slightly
        different from the value provided based on the ratio between the height
        of the window in screen pixels and desired number of game units to
        represent.

        When you set the height, the width will change as well.
        """
        return self._height

    @height.setter
    def height(self, target_height):
        self._set_dimensions(target_height=target_height)

    def point_is_visible(self, point: Vector) -> bool:
        """
        Determine if a given point is in view of the camera.

        :param point: A vector representation of a point in game units.
        :type point: Vector
        :return: Whether the point is in view or not.
        :rtype: bool
        """
        return (
            self.left <= point.x <= self.right
            and self.bottom <= point.y <= self.top
        )

    def translate_point_to_screen(self, point: Vector) -> Vector:
        """
        Convert a vector from game position to screen position.

        :param point: A vector in game units
        :type point: Vector
        :return: A vector in pixels.
        :rtype: Vector
        """
        return Vector(point.x - self.left, self.top - point.y) * self.pixel_ratio

    def translate_point_to_game_space(self, point: Vector) -> Vector:
        """
        Convert a vector from screen position to game position.

        :param point: A vector in pixels
        :type point: Vector
        :return: A vector in game units.
        :rtype: Vector
        """
        scaled = point / self.pixel_ratio
        return Vector(self.left + scaled.x, self.top - scaled.y)

    @property
    def bottom(self):
        return self.position.y - (self.height / 2)

    @property
    def left(self):
        return self.position.x - (self.width / 2)

    @property
    def right(self):
        return self.position.x + (self.width / 2)

    @property
    def top(self):
        return self.position.y + (self.height / 2)

    @property
    def top_left(self):
        return Vector(self.left, self.top)

    @property
    def top_right(self):
        return Vector(self.right, self.top)

    @property
    def bottom_left(self):
        return Vector(self.left, self.bottom)

    @property
    def bottom_right(self):
        return Vector(self.right, self.bottom)

    def _set_dimensions(self, target_width=None, target_height=None):
        # Set new pixel ratio
        viewport_width, viewport_height = self.viewport_dimensions
        if target_width is not None and target_height is not None:
            raise ValueError("Can only set one dimension at a time.")
        elif target_width is not None:
            game_unit_target = target_width
            pixel_value = viewport_width
        elif target_height is not None:
            game_unit_target = target_height
            pixel_value = viewport_height
        else:
            raise ValueError("Must set target_width or target_height")
        self.pixel_ratio = int(pixel_value / game_unit_target)
        self._width = viewport_width / self.pixel_ratio
        self._height = viewport_height / self.pixel_ratio
