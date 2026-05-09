from Entities.Item import Item
from Entities.Arrow import Arrow
from Engine import engine as e
import math

class Crossbow(Item):
    """
    Arbalète capable de tirer des flèches.
    """
    def __init__(self, x, y, w, h, bank, parent=None, world=None):
        super().__init__(x, y, w, h, bank, parent)
        self.world = world # Référence au monde pour ajouter les flèches
        self.rotation = 0
        self.radius = 5
        self.is_firing = False
        self.fire_timer = 0
        
    def update(self):
        super().update()
        if not self.picked_up or not self.parent: return
        
        # Calcul de l'angle vers la souris
        mouse_angle = math.atan2(e._global_mouse_pos[1] - self.parent.y, 
                                e._global_mouse_pos[0] - self.parent.x)
        
        # Tir
        if e.btnp(e.KEY_SPACE) and not self.is_firing:
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
        self.x = self.parent.x + self.radius * math.cos(mouse_angle)
        self.y = self.parent.y + self.radius * math.sin(mouse_angle)

    def draw(self):
        if not self.picked_up:
            # Sprite au sol (index 0, 12 d'après stuff.png)
            self.draw_image(0,9 )
        elif self.parent and self.parent.current_item == self:
            # Sprite en main (index 1, 12 si tir, sinon 0, 12)
            idx_x = 1 if self.is_firing else 0
            self.draw_image(idx_x, 9, rotate=-self.rotation)

    def fire(self, angle):
        """Crée une flèche dans le monde."""
        self.is_firing = True
        self.fire_timer = 15
        if self.world:
            # On crée la flèche à la position de l'arbalète
            arrow = Arrow(self.x, self.y, angle, self.bank)
            self.world.add(arrow)
