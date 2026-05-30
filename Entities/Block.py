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

    def take_damage(self, amount, world):
        if self.indestructible:
            return
        if self.blocking:
            super().take_damage(amount, world)

    def draw(self):
        if self.bank:
            self.draw_image(self.image_x, self.image_y)
        else:
            e.rect(self.x, self.y, self.w, self.h, self.color)
