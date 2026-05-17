import math

import pygame

from Engine import engine as e
from Entities.Item import Item


class Sword(Item):
    """
    Classe représentant une épée avec une capacité d'attaque (slash).
    """

    def __init__(self, x, y, w, h, bank, parent=None, speed=1):
        super().__init__(x, y, w, h, bank, parent, speed)
        self.rotation = 0
        self.radius = 5.5
        self.pos_angle = 0
        self.start_slash_angle = 0

        # État de l'animation d'attaque (slash)
        self.is_slashing = False
        self.slash_timer = 0
        self.slash_duration = 6
        self.p = 1  # Direction du balancement
        self.n = 1  # Côté de repos
        self.flipped = False  # État du miroir du sprite

    def update(self):
        super().update()

        if not self.picked_up or not self.parent:
            return

        # Déclencheur de l'attaque (seulement pour le joueur)
        if not hasattr(self.parent, "target"):
            if e.mouse_btnp(e.MOUSE_BUTTON_LEFT) and not self.is_slashing:
                self.slash()

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

        if self.is_slashing:
            # Progrès de l'animation de 0.0 à 1.0
            self.slash_timer -= 1
            progress = 1.0 - (self.slash_timer / self.slash_duration)

            # Arc de cercle : l'épée traverse d'un côté à l'autre
            arc_size = math.pi * 1.0
            self.pos_angle = self.start_slash_angle + (arc_size * progress * self.p)

            # Extension du bras (punch)
            self.radius = 7 + math.sin(progress * math.pi) * 5

            # La rotation suit l'angle de position
            self.rotation = math.degrees(self.pos_angle)

            if self.slash_timer <= 0:
                self.is_slashing = False
        else:
            # État de repos : l'épée suit la souris
            self.radius = 7
            target_pos_angle = mouse_angle - (math.pi / 2) * self.n

            # Interpolation fluide
            diff = (target_pos_angle - self.pos_angle + math.pi) % (
                2 * math.pi
            ) - math.pi
            self.pos_angle += diff * 0.2

            # La rotation suit l'angle de position
            self.rotation = math.degrees(self.pos_angle)

        self.x = self.parent.x + self.radius * math.cos(self.pos_angle)
        self.y = self.parent.y + self.radius * math.sin(self.pos_angle)

    def draw(self):
        if not self.picked_up:
            # Sprite au sol (index 3,9)
            self.draw_image(3, 8, offset=(2, 2))
            self.draw_image(3, 9, rotate=30)

        elif self.parent and self.parent.current_item == self:
            # Récupération de la portion de l'image
            sub = self.bank.subsurface((self.w * 2, self.h * 9, self.w, self.h))

            # On applique le flip horizontal pour refléter le sprite (réalisme)
            if self.flipped:
                sub = pygame.transform.flip(sub, True, False)

            # L'angle de dessin doit toujours pointer vers l'extérieur (rotation = pos_angle)
            # Pas besoin de 180° supplémentaire quand flipped car le flip s'occupe déjà de l'effet miroir
            e.blt(self.x, self.y, sub, 0, 0, self.w, self.h, rotate=-self.rotation + 90)

    def slash(self):
        self.is_slashing = True
        self.slash_timer = self.slash_duration

        # On capture l'angle actuel pour commencer le swing
        self.start_slash_angle = self.pos_angle

        # Direction du swing
        self.p = self.n

        # Changement de côté pour le prochain coup
        self.n *= -1
        self.flipped = not self.flipped
