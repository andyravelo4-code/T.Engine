import math

from Engine import engine as e
from Entities.Arrow import Arrow
from Entities.Item import Item


class Crossbow(Item):
    """
    Arbalète capable de tirer des flèches.
    """

    def __init__(self, x, y, w, h, bank, parent=None, world=None, damage=10,
                 shadow_pos=(0, 0), dropped_pos=(0, 9), held_idle_pos=(0, 9), held_fire_pos=(1, 9),
                 fire_timer=15, cooldown=30,name=""):
        super().__init__(x, y, w, h, bank, parent,
                         name=name, stackable=False, max_stack=1)
        self.world = world
        self.damage = damage
        self.shadow_pos = shadow_pos
        self.dropped_pos = dropped_pos
        self.held_idle_pos = held_idle_pos
        self.held_fire_pos = held_fire_pos
        self.rotation = 0
        self.radius = 5
        self.is_firing = False
        self.fire_duration = fire_timer
        self.fire_timer = 0
        self.cooldown = cooldown

    def update(self):
        super().update()
        if not self.picked_up or not self.parent:
            return

        # Calcul de l'angle vers la cible ou la souris
        if hasattr(self.parent, "target"):
            target_x = self.parent.target.x
            target_y = self.parent.target.y
        else:
            target_x = e._global_mouse_pos[0]
            target_y = e._global_mouse_pos[1]
            
        mouse_angle = math.atan2(
            target_y - self.parent.y,
            target_x - self.parent.x,
        )

        # Tir (seulement pour le joueur)
        if not hasattr(self.parent, "target"):
            if e.mouse_btnp(e.MOUSE_BUTTON_LEFT) and not self.is_firing:
                self.fire(mouse_angle)

        if self.is_firing:
            self.fire_timer -= 1
            # L'arbalète recule légèrement lors du tir (logique main.py test)
            self.radius -= 0.1
            if self.fire_timer <= 0:
                self.is_firing = False
                self.radius = 8
        else:
            self.radius = 8
        self.rotation = math.degrees(mouse_angle) + 90

        # Positionnement autour du parent
        self.x = int(self.parent.x + self.radius * math.cos(mouse_angle))
        self.y = int(self.parent.y + self.radius * math.sin(mouse_angle))

    def draw(self):
        if not self.picked_up:
            #self.draw_image(self.shadow_pos[0], self.shadow_pos[1], offset=(2, 2))
            self.draw_image(self.dropped_pos[0], self.dropped_pos[1])

        elif self.parent and self.parent.current_item == self:
            idx_x = self.held_fire_pos[0] if self.is_firing else self.held_idle_pos[0]
            idx_y = self.held_fire_pos[1] if self.is_firing else self.held_idle_pos[1]
            self.draw_image(idx_x, idx_y, rotate=-self.rotation)
            mouse_angle = math.atan2(
                e._global_mouse_pos[1] - (self.parent.y + self.parent.h / 2),
                e._global_mouse_pos[0] - (self.parent.x + self.parent.w / 2),
            )

    def fire(self, angle):
        """Crée une flèche dans le monde."""
        self.is_firing = True
        self.fire_timer = self.fire_duration
        if self.world:
            # On crée la flèche à la position de l'arbalète
            arrow = Arrow(self.x, self.y, angle, self.bank, world=self.world, shooter=self.parent, damage=self.damage)
            self.world.add(arrow)
