import pygame
from vec2d import vec2d

class Camera(object):
    def __init__(self, x, y, screen_width, screen_height):
        self.pos = vec2d(x, y)
        self.width, self.height = screen_width, screen_height

    def _get_left(self): return self.pos.x
    def _set_left(self, value): self.pos.x = value
    left = property(_get_left, _set_left, None, '')

    def _get_right(self): return self.pos.x + self.width
    def _set_right(self, value): self.pos.x = value - self.width
    right = property(_get_right, _set_right, None, '')

    def _get_top(self): return self.pos.y
    def _set_top(self, value): self.pos.y = value
    top = property(_get_top, _set_top, None, '')

    def _get_bottom(self): return self.pos.y + self.height
    def _set_bottom(self, value): self.pos.y = value - self.height
    bottom = property(_get_bottom, _set_bottom, None, '')

    def move(self, dx, dy): self.pos += (dx, dy)

    def pt_on_screen(self, pos):
        pos = vec2d(pos)
        return (self.left <= pos.x <= self.right and
                self.top <= pos.y <= self.bottom)

    def rect_on_screen(self, rectangle):
        right = rectangle.left + rectangle.width
        bottom = rectangle.top + rectangle.height
        return (pt_on_screen((rectangle.left, rectangle.top)) or
                pt_on_screen((rectangle.left, bottom)) or 
                pt_on_screen((right, rectangle.top)) or
                pt_on_screen((right, bottom)))


    def world_to_screen(self, world_pos): return world_pos - self.pos

    def screen_to_world(self, screen_pos): return screen_pos + self.pos