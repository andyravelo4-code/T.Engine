import math
import random

from Engine import engine as e
from Entities.Object import Object


class Arrow(Object):
    """
    Projectile tiré par l'arbalète.
    """

    def __init__(self, x, y, angle, bank, world=None, shooter=None, damage=10, sprite_pos=(0, 6)):
        super().__init__(x, y, 8, 8, bank)
        self.world = world
        self.shooter = shooter
        self.damage = damage
        self.sprite_pos = sprite_pos
        self.angle = angle
        self.speed = 4
        self.hitbox_inset=2
        self.lifetime = 60  # Disparaît après 60 frames
        self.offset = random.uniform(-0.1, 0.1)

    def update(self):
        super().update()
        self.x += math.cos(self.angle + self.offset) * self.speed
        self.y += math.sin(self.angle + self.offset) * self.speed

        if self.world:
            for entity in self.world.get_nearby(self.x + self.w / 2, self.y + self.h / 2, 12):
                if entity is self or entity is self.shooter or isinstance(entity, Arrow):
                    continue
                if not hasattr(entity, 'take_damage'):
                    continue
                if not entity.is_living and not getattr(entity, 'blocking', False):
                    continue

                dx = entity.x + entity.w/2 - self.x
                dy = entity.y + entity.h/2 - self.y
                if dx * dx + dy * dy < 64:
                    entity.take_damage(self.damage, self.world, angle=self.angle)
                    if hasattr(e, 'active_camera'):
                        e.active_camera.shake(3, 2)
                        if entity.is_living:
                            e.active_camera.flash((255, 180, 180), 25, 4)
                    self.lifetime = 0
                    break

        self.lifetime -= 1
        # Note : La suppression du monde doit être gérée par le World ou ici via une propriété

    def draw(self):
        self.draw_image(self.sprite_pos[0], self.sprite_pos[1], rotate=int(-math.degrees(self.angle) + self.offset + 90))
