import math
import Engine.engine
from Engine import engine
from Entities.Block import Block
from Entities.Player import Player
import math

class FloatingText:
    def __init__(self, x, y, text, color, lifetime):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime


class World:
    """
    Conteneur global pour toutes les entités du jeu.
    Gère la mise à jour et le dessin de chaque entité.
    """

    def __init__(self):
        self.entities = []
        self.active_npc = None
        self.floating_texts = []
        self.player = None

    def add_floating_text(self, x, y, text, color, lifetime):
        self.floating_texts.append(FloatingText(x, y, text, color, lifetime))

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
        if not self.player :
            for e in self.entities :
                if isinstance(e, Player):
                    self.player = e 
                    break
        self.update_active_npc()
        for entity in list(self.entities):
            entity.update()
            if hasattr(entity, "lifetime") and entity.lifetime <= 0:
                self.remove(entity)

        for ft in list(self.floating_texts):
            ft.y -= 0.3
            ft.lifetime -= 1
            if ft.lifetime <= 0:
                self.floating_texts.remove(ft)

    def draw(self):
        """Dessine d'abord les blocs (fond), puis les entités triées par y."""
        cam_x = engine.graphics._camera_x
        cam_y = engine.graphics._camera_y
        sw = engine.width()
        sh = engine.height()

        blocks = [e for e in self.entities if isinstance(e, Block)]
        for e in blocks:
            sx = e.x + cam_x
            sy = e.y + cam_y
            dist = math.dist((-cam_x+engine.width()/2,-cam_y+engine.height()/2),(e.x,e.y))
            #dist1 = math.dist((engine.mouse_x()-cam_x,engine.mouse_y()-cam_y),(e.x,e.y))
            if sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh and( dist < 60) :#or sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh and dist < 30 :
                e.draw()

        others = [e for e in self.entities if not isinstance(e, Block)]
        for e in sorted(others, key=lambda e: e.y):
            dist = math.dist((-cam_x+engine.width()/2,-cam_y+engine.height()/2),(e.x,e.y))
            #dist1 = math.dist((engine.mouse_x()-cam_x,engine.mouse_y()-cam_y),(e.x,e.y))
            if  dist < 60:
                e.draw()
        for ft in self.floating_texts:
            font = engine.default_font(6)
            surf = font.render(ft.text, False, ft.color[:3])
            surf.set_alpha(int(255 * ft.lifetime / ft.max_lifetime))
            engine.graphics.screen.blit(surf,
                (ft.x + engine.graphics._camera_x - surf.get_width() // 2,
                 ft.y + engine.graphics._camera_y))
        