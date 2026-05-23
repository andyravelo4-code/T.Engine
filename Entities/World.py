import math
import Engine.engine
from Engine import engine


class World:
    """
    Conteneur global pour toutes les entités du jeu.
    Gère la mise à jour et le dessin de chaque entité.
    """

    def __init__(self):
        self.entities = []
        self.active_npc = None

    def add(self, entity):
        """Ajoute une entité au monde."""
        if entity not in self.entities:
            self.entities.append(entity)

    def remove(self, entity):
        """Retire une entité du monde."""
        if entity in self.entities:
            self.entities.remove(entity)
        if entity is self.active_npc:
            self.active_npc = None

    def update_active_npc(self):
        """Maintient le NPC le plus proche de sa cible comme actif."""
        if self.active_npc is not None and self.active_npc in self.entities:
            if hasattr(self.active_npc, 'target') and self.active_npc.target:
                dist = math.hypot(
                    self.active_npc.x - self.active_npc.target.x,
                    self.active_npc.y - self.active_npc.target.y
                )
                if dist < self.active_npc.detection_radius:
                    return

        closest = None
        closest_dist = float('inf')
        for entity in self.entities:
            if hasattr(entity, 'aggressive') and entity.aggressive and hasattr(entity, 'target') and entity.target:
                dist = math.hypot(entity.x - entity.target.x, entity.y - entity.target.y)
                if dist < entity.detection_radius and dist < closest_dist:
                    closest = entity
                    closest_dist = dist

        self.active_npc = closest

    def update(self):
        """Met à jour toutes les entités et supprime celles qui ont expiré."""
        self.update_active_npc()
        for entity in list(self.entities):
            entity.update()
            if hasattr(entity, "lifetime") and entity.lifetime <= 0:
                self.remove(entity)

    def draw(self):
        """Dessine toutes les entités."""
        engine.circb(
            engine._global_mouse_pos[0],
            engine._global_mouse_pos[1],
            4,
            (255, 255, 255,50),
        )
        for entity in sorted(self.entities, key=lambda e: e.y):
            entity.draw()
