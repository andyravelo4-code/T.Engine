import random
import math
from Entities.Block import Block
from Entities.Npc import Npc
from Entities.Sword import Sword
from Entities.Crossbow import Crossbow


class Map:
    BIOME_BG = {
        "cave":    (20, 18, 25),
        "dungeon": (30, 30, 35),
        "island":  (25, 40, 55),
    }

    # Fallback colors when no tile_images dict is provided
    FALLBACK_COLORS = {
        "cave":    {1: (80, 75, 65), 3: (100, 220, 255)},
        "dungeon": {1: (100, 100, 100), 3: (80, 80, 80), 4: (60, 55, 50)},
        "island":  {2: (10, 55, 85), 3: (120, 105, 70), 4: (70, 65, 60)},
    }

    def __init__(self, world, tile_size=8):
        self.world = world
        self.tile_size = tile_size
        self.grid = []
        self.width = 0
        self.height = 0
        self.biome = None
        self.bg_color = (0, 0, 0)

    def generate(self, biome, map_width, map_height, npc_count=5, player=None, frames_dicts=None, img2=None, tile_images=None):
        self.biome = biome
        self.bg_color = self.BIOME_BG.get(biome, (0, 0, 0))
        self.width = map_width
        self.height = map_height
        self.grid = [[0] * map_width for _ in range(map_height)]

        {
            "cave": self._gen_cave,
            "dungeon": self._gen_dungeon,
            "island": self._gen_island,
        }.get(biome, lambda: None)()

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts and img2:
            self._spawn_npcs(npc_count, player, frames_dicts)
            self._place_items(img2)

    def _gen_cave(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1 if random.random() < 0.35 else 0

        for _ in range(3):
            new = [row[:] for row in self.grid]
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    walls = sum(
                        1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if (dx or dy) and self.grid[y + dy][x + dx] == 1
                    )
                    if self.grid[y][x] == 1:
                        new[y][x] = 1 if walls >= 4 else 0
                    else:
                        new[y][x] = 1 if walls >= 5 else 0
            self.grid = new

        # Cristaux décoratifs (tuile 3)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1 and random.random() < 0.06:
                    self.grid[y][x] = 3

        cx, cy = self.width // 2, self.height // 2
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < self.height and 0 <= xx < self.width:
                    self.grid[yy][xx] = 0

    def _gen_dungeon(self):
        self.grid = [[1] * self.width for _ in range(self.height)]
        rooms = []

        gap = 3
        base_w, base_h = 5, 5
        cols = max(2, self.width // (base_w + gap))
        rows = max(2, self.height // (base_h + gap))

        for gy in range(rows):
            for gx in range(cols):
                rx = gx * (base_w + gap) + random.randint(0, 1)
                ry = gy * (base_h + gap) + random.randint(0, 1)
                rw = base_w + random.randint(-1, 2)
                rh = base_h + random.randint(-1, 2)
                if rx + rw >= self.width - 1 or ry + rh >= self.height - 1:
                    continue
                rooms.append((rx, ry, rw, rh))
                for y in range(ry, ry + rh):
                    for x in range(rx, rx + rw):
                        self.grid[y][x] = 0

        # Piliers dans les salles (tuile 3)
        for rx, ry, rw, rh in rooms:
            for _ in range(random.randint(1, 3)):
                px = rx + random.randint(1, max(1, rw - 2))
                py = ry + random.randint(1, max(1, rh - 2))
                if self.grid[py][px] == 0:
                    self.grid[py][px] = 3

        # Gravats dans les couloirs (tuile 4)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 0 and random.random() < 0.04:
                    if any(self.grid[y + dy][x + dx] == 1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                        self.grid[y][x] = 4

        # Relie les salles adjacentes (droite et bas) par des couloirs courts
        for gy in range(rows):
            for gx in range(cols):
                i = gy * cols + gx
                if i >= len(rooms):
                    continue
                rx, ry, rw, rh = rooms[i]
                cx, cy = rx + rw // 2, ry + rh // 2

                if gx + 1 < cols and i + 1 < len(rooms):
                    nx = rooms[i + 1][0] + rooms[i + 1][2] // 2
                    for x in range(min(cx, nx), max(cx, nx) + 1):
                        self.grid[cy][x] = 0

                if gy + 1 < rows and i + cols < len(rooms):
                    ny = rooms[i + cols][1] + rooms[i + cols][3] // 2
                    for y in range(min(cy, ny), max(cy, ny) + 1):
                        self.grid[y][cx] = 0

    def _gen_island(self):
        cx, cy = self.width / 2, self.height / 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        h = [[0.0] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                h[y][x] = 1.0 - math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_dist + random.uniform(-0.25, 0.25)

        for _ in range(3):
            h2 = [row[:] for row in h]
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    h2[y][x] = sum(h[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
            h = h2

        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 2 if h[y][x] < 0.35 else 3

        # Rochers (tuile 4, bloquant) éparpillés sur le sable
        for y in range(2, self.height - 2):
            for x in range(2, self.width - 2):
                if self.grid[y][x] == 3 and random.random() < 0.06:
                    self.grid[y][x] = 4

    NON_BLOCKING_TILES = {
        "island": {2, 3},  # eau et sable traversables
    }

    def _build_blocks(self, tile_images=None):
        fallback = self.FALLBACK_COLORS.get(self.biome, {})
        walkable = self.NON_BLOCKING_TILES.get(self.biome, set())

        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile == 0:
                    continue

                if tile_images and tile in tile_images:
                    cfg = tile_images[tile]
                    block = Block(
                        x * self.tile_size, y * self.tile_size,
                        self.tile_size, self.tile_size,
                        cfg["bank"],
                        image_x=cfg.get("image_x", 0),
                        image_y=cfg.get("image_y", 0),
                        color=cfg.get("color"),
                    )
                else:
                    color = fallback.get(tile)
                    if not color:
                        continue
                    block = Block(
                        x * self.tile_size, y * self.tile_size,
                        self.tile_size, self.tile_size,
                        None, color=color,
                    )

                if tile in walkable:
                    block.blocking = False
                self.world.add(block)

    def get_spawn_point(self):
        cx, cy = self.width // 2, self.height // 2
        for r in range(max(self.width, self.height)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < self.width and 0 <= y < self.height and self._is_walkable(self.grid[y][x]):
                        return (x * self.tile_size, y * self.tile_size)
        return (cx * self.tile_size, cy * self.tile_size)

    def _is_walkable(self, tile):
        if tile == 0:
            return True
        walkable = self.NON_BLOCKING_TILES.get(self.biome, set())
        return tile in walkable

    def _spawn_npcs(self, count, player, frames_dicts):
        spawned = 0
        attempts = 0
        while spawned < count and attempts < 2000:
            attempts += 1
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self._is_walkable(self.grid[y][x]):
                self.world.add(Npc(
                    x * self.tile_size, y * self.tile_size,
                    self.tile_size, self.tile_size,
                    target=player, frames_dict=random.choice(frames_dicts),
                    world=self.world,
                ))
                spawned += 1

    def _place_items(self, img):
        for cls in (Sword, Crossbow, Crossbow):
            for _ in range(500):
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                if self._is_walkable(self.grid[y][x]):
                    item = cls(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, img)
                    if hasattr(item, "world"):
                        item.world = self.world
                    self.world.add(item)
                    break
