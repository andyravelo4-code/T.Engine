from Entities.Object import Object
from Engine import engine as e

class Item(Object):
    def __init__(self, x, y, w, h, bank, parent=None, speed=1,
                 name="Item", stackable=True, max_stack=64, quantity=1):
        if isinstance(bank, int) and bank < len(e.resources.images):
            bank = e.resources.images[bank]

        super().__init__(x, y, w, h, bank, speed)
        self.parent = parent
        self.picked_up = False
        self.world = None
        self.name = name
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = quantity

    def can_stack_with(self, other):
        return (self.stackable and other.stackable
                and type(self) is type(other)
                and self.name == other.name
                and self.quantity < self.max_stack)

    def stack_space(self):
        return self.max_stack - self.quantity if self.stackable else 0

    def split(self, amount):
        take = min(amount, self.quantity)
        self.quantity -= take
        return take

    def update(self):
        super().update()

    def draw(self):
        if not self.picked_up:
            self.draw_image(0, 0, rotate=30)
        elif self.parent and self.parent.current_item == self:
            pass
