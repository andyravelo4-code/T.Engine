from Entities.Object import Object
from Engine import engine as e

class Block(Object):
    def __init__(self, x, y, w, h, bank, image_x=0, image_y=0):
        super().__init__(x, y, w, h, bank)
        self.blocking = True
        self.image_x = image_x
        self.image_y = image_y

    def draw(self):
        # Draw the sprite from the bank
        if self.bank:
            self.draw_image(self.image_x, self.image_y)
        else:
            e.rect(self.x, self.y, self.w, self.h, (100, 100, 100))
