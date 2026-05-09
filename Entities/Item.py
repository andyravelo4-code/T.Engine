from Entities.Object import Object
from Engine import engine as e

class Item(Object):
    """
    Classe de base pour tous les objets collectables.
    """
    def __init__(self, x, y, w, h, bank, parent=None, speed=1):
        # Conversion de la banque d'images en surface si nécessaire
        if isinstance(bank, int) and bank < len(e.resources.images):
            bank = e.resources.images[bank]
            
        super().__init__(x, y, w, h, bank, speed)
        self.parent = parent
        self.picked_up = False

    def update(self):
        super().update()
        # Si l'objet n'est pas ramassé, il reste à sa position dans le monde
        # Si ramassé, sa logique de position est gérée par la sous-classe (Sword, etc.)

    def draw(self):
        # Si l'objet est au sol, on le dessine à sa position x, y
        if not self.picked_up:
            # Par défaut, on dessine le sprite (0, 0) de la banque d'images de l'item
            # Les sous-classes peuvent outrepasser cela.
            self.draw_image(0, 0)
        elif self.parent and self.parent.current_item == self:
            # Si porté et actif, le dessin est géré par la sous-classe
            pass
