from math import degrees
import math
from Engine import engine as e
from Entities.Object import Object

def angle(x1, y1, x2, y2):
    """Retourne l'angle en radians entre deux points."""
    return math.atan2(y2 - y1, x2 - x1)

def limit(val, min_val, max_val):
    """Limite une valeur entre min et max."""
    return max(min_val, min(max_val, val))

class Item(Object):
    def __init__(self, x, y, w, h, bank,parent : Object, speed=1):
        super().__init__(x, y, w, h, bank, speed)
        self.parent=parent
        self.rotation=0
    def update(self):
        super().update()
        dir=angle(self.parent.x,self.parent.y,e._global_mouse_pos[0],e._global_mouse_pos[1])-math.pi/1.5
        self.x = self.parent.x + 7 * math.cos(dir)
        self.y = self.parent.y + 7 * math.sin(dir)
        self.rotation=math.degrees(dir)+50
    def draw(self):
        super().draw()
        self.draw_image(3,9,rotate=-self.rotation)

