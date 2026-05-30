import math

import pygame

from Engine import engine as e
from Entities.Item import Item


class Sword(Item):
    """
    Classe représentant une épée avec une capacité d'attaque (slash).
    """

    def __init__(self, x, y, w, h, bank, parent=None, speed=1, damage=25,
                 shadow_pos=(0, 0), dropped_pos=(3, 9), held_pos=(2, 9),
                 cooldown=20,name=""):
        super().__init__(x, y, w, h, bank, parent, speed,
                         name=name, stackable=False, max_stack=1)
        self.damage = damage
        self.shadow_pos = shadow_pos
        self.dropped_pos = dropped_pos
        self.held_pos = held_pos
        self.rotation = 0
        self.radius = 5.5
        self.pos_angle = 0
        self.start_slash_angle = 0
        self.cooldown = cooldown

        # État de l'animation d'attaque (slash)
        self.is_slashing = False
        self.slash_timer = 0
        self.slash_duration = 6
        self.p = 1  # Direction du balancement
        self.n = 1  # Côté de repos
        self.flipped = False  # État du miroir du sprite
        self.hit_entities = []

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

            if self.world:
                for entity in self.world.entities:
                    if entity is self or entity is self.parent or not hasattr(entity, 'take_damage'):
                        continue
                    if not entity.is_living and not getattr(entity, 'blocking', False):
                        continue
                    dist = math.hypot(entity.x + entity.w/2 - self.x, entity.y + entity.h/2 - self.y)
                    if dist < 12 and entity not in self.hit_entities:
                            self.hit_entities.append(entity)
                            entity.take_damage(self.damage, self.world)
                            if hasattr(e, 'active_camera'):
                                e.active_camera.shake(5, 3)
                                if getattr(entity, 'is_living', False):
                                    e.active_camera.flash((255, 230, 150), 30, 5)

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
            self.draw_image(self.shadow_pos[0], self.shadow_pos[1], offset=(2, 2))
            self.draw_image(self.dropped_pos[0], self.dropped_pos[1], rotate=30)

        elif self.parent and self.parent.current_item == self:
            # Draw slash arc
            if self.is_slashing:
                progress = 1.0 - (self.slash_timer / self.slash_duration)
                alpha = int(255 * (1 - progress))
                surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                
                center = (32, 32)
                radius = 12+ progress * 5
                
                current_angle = self.start_slash_angle + (math.pi * 1.0 * progress * self.p)
                points = []
                
                # Outer arc
                for i in range(-70, 71, 10):
                    rad = math.radians(i) + current_angle
                    px = center[0] + math.cos(rad) * radius
                    py = center[1] + math.sin(rad) * radius
                    points.append((px, py))
                
                # Inner arc
                for i in range(70, -71, -10):
                    rad = math.radians(i) + current_angle
                    thickness = 3 * math.cos(math.radians(i / 70 * 90))
                    r = radius - thickness
                    px = center[0] + math.cos(rad) * r
                    py = center[1] + math.sin(rad) * r
                    points.append((px, py))
                
                if len(points) >= 3:
                    pygame.draw.polygon(surf, (255, 255, 255, (alpha+50)%255), points)
                
                e.graphics.screen.blit(surf, (self.parent.x + self.parent.w/2 - 32 + e.graphics._camera_x, self.parent.y + self.parent.h/2 - 32 + e.graphics._camera_y))

            # Récupération de la portion de l'image
            sub = self.bank.subsurface((self.w * self.held_pos[0], self.h * self.held_pos[1], self.w, self.h))

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
        self.hit_entities = []
