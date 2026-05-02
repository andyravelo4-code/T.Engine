import math
from Engine import engine as e
from Entities.Object import Object

# ----------------------------------------------------------------------
# Fonctions utilitaires (recopiées du script original)
# ----------------------------------------------------------------------
def angle(x1, y1, x2, y2):
    """Retourne l'angle en radians entre deux points."""
    return math.atan2(y2 - y1, x2 - x1)

def limit(val, min_val, max_val):
    """Limite une valeur entre min et max."""
    return max(min_val, min(max_val, val))

class Item(Object):
    def __init__(self, x, y, w, h, bank, speed=1):
        super().__init__(x, y, w, h, bank, speed)
    def update(self):
        super().update()
    def draw(self):
        super().draw()

