import math
import Engine.engine
from Engine import engine
from Entities.Block import Block
from Entities.Player import Player
from Entities.Particle import Particle
from Entities.Light import Light, render_light_overlay

class SpatialHash:
    def __init__(self, cell_size=16):
        self.cell_size = cell_size
        self.cells = {}

    def clear(self):
        self.cells.clear()

    def add(self, entity):
        cx = int((entity.x + entity.w / 2) // self.cell_size)
        cy = int((entity.y + entity.h / 2) // self.cell_size)
        key = (cx, cy)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(entity)

    def get_near(self, x, y, radius):
        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)
        r = int(radius // self.cell_size) + 1
        result = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                cell = self.cells.get((cx + dx, cy + dy))
                if cell:
                    result.extend(cell)
        return result


class FloatingText:
    def __init__(self, x, y, text, color, lifetime):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self._surf = None

    def get_surface(self):
        if self._surf is None:
            font = engine.default_font(6)
            self._surf = font.render(self.text, False, self.color[:3])
        self._surf.set_alpha(int(255 * self.lifetime / self.max_lifetime))
        return self._surf


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
        self.spatial = SpatialHash(16)
        self._cam_x = 0.0
        self._cam_y = 0.0
        self._cam_w = 0
        self._cam_h = 0
        self.lights = []

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

    def get_nearby(self, x, y, radius):
        return self.spatial.get_near(x, y, radius)

    def update_active_npc(self):
        """Maintient le NPC le plus proche de sa cible comme actif."""
        if self.active_npc is not None and self.active_npc in self.entities:
            if hasattr(self.active_npc, 'target') and self.active_npc.target:
                dx = self.active_npc.x - self.active_npc.target.x
                dy = self.active_npc.y - self.active_npc.target.y
                dr2 = self.active_npc.detection_radius ** 2
                if dx * dx + dy * dy < dr2:
                    return

        closest = None
        closest_dist2 = float('inf')
        for entity in self.entities:
            if not (hasattr(entity, 'aggressive') and entity.aggressive and hasattr(entity, 'target') and entity.target):
                continue
            dx = entity.x - entity.target.x
            dy = entity.y - entity.target.y
            d2 = dx * dx + dy * dy
            dr2 = entity.detection_radius ** 2
            if d2 < dr2 and d2 < closest_dist2:
                closest = entity
                closest_dist2 = d2

        self.active_npc = closest

    def update(self):
        """Met à jour toutes les entités et supprime celles qui ont expiré."""
        if not self.player:
            for e in self.entities:
                if isinstance(e, Player):
                    self.player = e
                    break

        self.spatial.clear()
        for e in self.entities:
            self.spatial.add(e)

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

        for light in self.lights:
            light.update(self)

    def draw(self):
        """Dessine d'abord les blocs (fond), puis les entités triées par y."""
        cam_x = engine.graphics._camera_x
        cam_y = engine.graphics._camera_y
        sw = engine.width()
        sh = engine.height()
        cx = -cam_x + sw / 2
        cy = -cam_y + sh / 2

        near = self.spatial.get_near(cx, cy, 100)
        d2max = 8600

        floor_blocks = [e for e in near if isinstance(e, Block) and getattr(e, 'is_floor', False)]
        for e in floor_blocks:
            sx = e.x + cam_x
            sy = e.y + cam_y
            if sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh:
                dx = e.x + e.w / 2 - cx
                dy = e.y + e.h / 2 - cy
                if dx * dx + dy * dy < d2max:
                    e.draw()
        floor_blocks = [e for e in near if isinstance(e, Particle) ]
        for e in floor_blocks:
            sx = e.x + cam_x
            sy = e.y + cam_y
            if sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh:
                dx = e.x + e.w / 2 - cx
                dy = e.y + e.h / 2 - cy
                if dx * dx + dy * dy < d2max:
                    e.draw()
        fixed_blocks = [e for e in near if isinstance(e, Block) and not getattr(e, 'pushable', False) and not getattr(e, 'is_floor', False)]
        for e in sorted(fixed_blocks, key=lambda e: e.y):
            sx = e.x + cam_x
            sy = e.y + cam_y
            if sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh:
                dx = e.x + e.w / 2 - cx
                dy = e.y + e.h / 2 - cy
                if dx * dx + dy * dy < d2max:
                    e.draw()

        others = [e for e in near if not isinstance(e, Block) and not isinstance(e,Particle)]
        for e in sorted(others, key=lambda e: e.y):
            dx = e.x + e.w / 2 - cx
            dy = e.y + e.h / 2 - cy
            if dx * dx + dy * dy < d2max:
                e.draw()

        pushable_blocks = [e for e in near if isinstance(e, Block) and getattr(e, 'pushable', False)]
        for e in sorted(pushable_blocks, key=lambda e: e.y):
            sx = e.x + cam_x
            sy = e.y + cam_y
            dx = e.x + e.w / 2 - cx
            dy = e.y + e.h / 2 - cy
            if dx * dx + dy * dy < d2max and (sx + e.w > 0 and sx < sw and sy + e.h > 0 and sy < sh):
                e.draw()
            else : continue

        for ft in self.floating_texts:
            surf = ft.get_surface()
            engine.graphics.screen.blit(surf,
                (ft.x + engine.graphics._camera_x - surf.get_width() // 2,
                 ft.y + engine.graphics._camera_y))

        if self.lights:
            overlay = render_light_overlay(self, cam_x, cam_y)
            engine.graphics.screen.blit(overlay, (0, 0))
        