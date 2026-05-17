import Engine.engine
from Engine import engine


class World:
    """
    Conteneur global pour toutes les entités du jeu.
    Gère la mise à jour et le dessin de chaque entité.
    """

    def __init__(self):
        self.entities = []

    def add(self, entity):
        """Ajoute une entité au monde."""
        if entity not in self.entities:
            self.entities.append(entity)

    def remove(self, entity):
        """Retire une entité du monde."""
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self):
        """Met à jour toutes les entités et supprime celles qui ont expiré."""
        for entity in list(self.entities):
            entity.update()
            # Suppression automatique si l'entité a une durée de vie épuisée
            if hasattr(entity, "lifetime") and entity.lifetime <= 0:
                self.remove(entity)

    def draw(self):
        """Dessine toutes les entités."""
        engine.circb(
            engine._global_mouse_pos[0],
            engine._global_mouse_pos[1],
            4,
            (255, 255, 255),
        )
        for entity in sorted(self.entities, key=lambda e: e.y):
            entity.draw()
