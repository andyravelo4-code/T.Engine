from Entities.Object import Object
from Engine import engine as e
import math

class Arrow(Object):
    """
    Projectile tiré par l'arbalète.
    """
    def __init__(self, x, y, angle, bank):
        super().__init__(x, y, 8, 8, bank)
        self.angle = angle
        self.speed = 4
        self.lifetime = 60 # Disparaît après 60 frames

    def update(self):
        super().update()
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        self.lifetime -= 1
        # Note : La suppression du monde doit être gérée par le World ou ici via une propriété

    def draw(self):
        # Utilise le sprite de la flèche (index 3, 12 d'après stuff.png)
        # On ajoute 90 degrés car le sprite est orienté vers le haut par défaut dans cette planche ?
        # Dans main.py test, rotate = r (le rt calculé)
        self.draw_image(4, 6, rotate=-math.degrees(self.angle) + 90)
