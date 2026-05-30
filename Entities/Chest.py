import random
from Engine import engine as e
from Entities.Object import Object


class Chest(Object):
    def __init__(self, x, y, w, h, bank, image_x=0, image_y=0, items=None, color=None):
        super().__init__(x, y, w, h, bank)
        self.blocking = True
        self.image_x = image_x
        self.image_y = image_y
        self.items = items or []
        self.color = color if color else (160, 130, 50)
        self._shake_timer = 0
        self._shake_intensity = 0
        self._shake_ox = 0
        self._shake_oy = 0

    def take_damage(self, amount, world):
        self.health -= amount
        self._shake_timer = 12
        self._shake_intensity = 3
        died = self.health <= 0
        if died:
            self._spawn_item(world)
            try:
                from Entities.Particle import spawn_hit, spawn_bones
                spawn_hit(self.x + self.w / 2, self.y + self.h / 2, world, amount=5)
                spawn_bones(self.x + self.w / 2, self.y + self.h / 2, world)
            except ImportError:
                pass
            world.remove(self)
        else:
            try:
                from Entities.Particle import spawn_hit
                spawn_hit(self.x + self.w / 2, self.y + self.h / 2, world, amount=2)
            except ImportError:
                pass

    def _spawn_item(self, world):
        if not self.items:
            return
        cfg = random.choice(self.items)
        cls = cfg["cls"]
        bank = cfg.get("bank", self.bank)
        item_kwargs = {k: v for k, v in cfg.items() if k not in ("cls", "bank")}
        item = cls(
            self.x, self.y,
            self.w, self.h,
            bank, **item_kwargs
        )
        if hasattr(item, "world"):
            item.world = world
        world.add(item)

    def update(self):
        if self._shake_timer > 0:
            self._shake_timer -= 1
            if self._shake_timer % 2 == 0 and self._shake_intensity > 0:
                self._shake_intensity = max(0, self._shake_intensity - 1)
            self._shake_ox = random.randint(-self._shake_intensity, self._shake_intensity)
            self._shake_oy = random.randint(-self._shake_intensity, self._shake_intensity)
        else:
            self._shake_ox = 0
            self._shake_oy = 0

    def draw(self):
        if self.bank:
            self.draw_image(self.image_x, self.image_y, offset=(self._shake_ox, self._shake_oy))
        else:
            e.rect(
                self.x + self._shake_ox,
                self.y + self._shake_oy,
                self.w, self.h,
                self.color,
            )
