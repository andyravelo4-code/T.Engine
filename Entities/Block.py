from Entities.Object import Object
from Engine import engine as e

class Block(Object):
    def __init__(self, x, y, w, h, bank, image_x=0, image_y=0, color=None, indestructible=False):
        super().__init__(x, y, w, h, bank)
        self.blocking = True
        self.image_x = image_x
        self.image_y = image_y
        self.color = color if color else (100, 100, 100)
        self.indestructible = indestructible

    def take_damage(self, amount, world, angle=None):
        if self.indestructible:
            return
        if self.blocking:
            super().take_damage(amount, world, angle=angle)

    def push_back(self, px, py, pw, ph, speed):
        if not (self.x < px + pw and self.x + self.w > px and
                self.y < py + ph and self.y + self.h > py):
            return 'none'
        overlap_left = (self.x + self.w) - px
        overlap_right = (px + pw) - self.x
        overlap_up = (self.y + self.h) - py
        overlap_down = (py + ph) - self.y
        if min(overlap_left, overlap_right) < min(overlap_up, overlap_down):
            if overlap_left < overlap_right:
                self.x -= speed
                return 'left'
            else:
                self.x += speed
                return 'right'
        else:
            if overlap_up < overlap_down:
                self.y -= speed
                return 'up'
            else:
                self.y += speed
                return 'down'

    def draw(self):
        if self.bank:
            self.draw_image(self.image_x, self.image_y)
        else:
            e.rect(self.x, self.y, self.w, self.h, self.color)
