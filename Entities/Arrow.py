import math
import random

from Engine import engine as e
from Entities.Object import Object


class Arrow(Object):
    """
    Projectile tiré par l'arbalète.
    """

    def __init__(self, x, y, angle, bank, world=None, shooter=None):
        super().__init__(x, y, 8, 8, bank)
        self.world = world
        self.shooter = shooter
        self.angle = angle
        self.speed = 4
        self.lifetime = 60  # Disparaît après 60 frames
        self.offset = random.uniform(-0.1, 0.1)

    def update(self):
        super().update()
        self.x += math.cos(self.angle + self.offset) * self.speed
        self.y += math.sin(self.angle + self.offset) * self.speed

        if self.world:
            for entity in self.world.entities:
                if entity != self and entity != self.shooter and not isinstance(entity, Arrow) and hasattr(entity, 'take_damage'):
                    # don't hit the shooter
                    if hasattr(entity, 'current_item') and hasattr(entity, 'items'):
                        # this is likely a player or npc. Check if they shot it.
                        # For simplicity, if we are within range:
                        dist = math.hypot(entity.x + entity.w/2 - self.x, entity.y + entity.h/2 - self.y)
                        if dist < 8:
                            entity.take_damage(10, self.world)
                            try:
                                from Entities.Particle import spawn_hit
                                spawn_hit(self.x, self.y, self.world, amount=3)
                                if hasattr(e, 'active_camera'):
                                    e.active_camera.shake(3, 2)
                            except Exception:
                                pass
                            self.lifetime = 0
                            break

        self.lifetime -= 1
        # Note : La suppression du monde doit être gérée par le World ou ici via une propriété

    def draw(self):
        # Utilise le sprite de la flèche (index 3, 12 d'après stuff.png)
        # On ajoute 90 degrés car le sprite est orienté vers le haut par défaut dans cette planche ?
        # Dans main.py test, rotate = r (le rt calculé)
        self.draw_image(4, 6, rotate=int(-math.degrees(self.angle) + self.offset + 90))
