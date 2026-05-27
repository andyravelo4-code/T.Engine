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
        "plains":  (45, 60, 45),
        "hills":   (40, 55, 40),
        "rocky_plains": (45, 45, 50),
        "forest":  (35, 55, 35),
        "desert":  (60, 55, 35),
        "mountains": (45, 45, 55),
    }

    FALLBACK_COLORS = {
        "cave":    {1: (80, 75, 65), 3: (100, 220, 255)},
        "dungeon": {1: (100, 100, 100), 3: (80, 80, 80), 4: (60, 55, 50)},
        "island":  {2: (10, 55, 85), 3: (120, 105, 70), 4: (70, 65, 60)},
        "plains":  {2: (10, 55, 85), 3: (60, 130, 60), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30)},
        "hills":   {2: (10, 55, 85), 3: (55, 120, 55), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30)},
        "rocky_plains": {2: (10, 55, 85), 1: (100, 100, 100), 4: (120, 115, 110), 5: (200, 180, 120)},
        "forest":  {2: (10, 55, 85), 3: (40, 100, 40), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30)},
        "desert":  {2: (10, 55, 85), 5: (200, 180, 120), 4: (160, 140, 100)},
        "mountains": {2: (10, 55, 85), 1: (140, 140, 150), 4: (120, 115, 110), 5: (200, 180, 120)},
    }

    NON_BLOCKING_TILES = {
        "island": {2, 3},
        "plains": {3, 5, 6},
        "hills": {3, 5, 6},
        "rocky_plains": {1, 5},
        "forest": {3, 5, 6},
        "desert": {5},
        "mountains": {5},
    }

    BIOME_CONFIG = {
        "plains": {
            "surface": 3,
            "decoration": None,
            "decoration_chance": 0.02,
            "base_height": 0.38,
            "height_amp": 0.18,
        },
        "hills": {
            "surface": 3,
            "decoration": 4,
            "decoration_chance": 0.04,
            "base_height": 0.50,
            "height_amp": 0.28,
        },
        "rocky_plains": {
            "surface": 1,
            "decoration": 4,
            "decoration_chance": 0.08,
            "base_height": 0.45,
            "height_amp": 0.18,
        },
        "forest": {
            "surface": 3,
            "decoration": 7,
            "decoration_chance": 0.14,
            "base_height": 0.42,
            "height_amp": 0.22,
        },
        "desert": {
            "surface": 5,
            "decoration": 4,
            "decoration_chance": 0.02,
            "base_height": 0.35,
            "height_amp": 0.10,
        },
        "mountains": {
            "surface": 1,
            "decoration": None,
            "decoration_chance": 0.03,
            "base_height": 0.65,
            "height_amp": 0.35,
        },
    }

    def __init__(self, world, tile_size=8):
        self.world = world
        self.tile_size = tile_size
        self.grid = []
        self.width = 0
        self.height = 0
        self.biome = None
        self.bg_color = (0, 0, 0)
        self.biome_grid = None

    def generate(self, biome, map_width, map_height, npc_count=5, player=None, frames_dicts=None, img2=None, tile_images=None):
        self.biome = biome
        self.bg_color = self.BIOME_BG.get(biome, (0, 0, 0))
        self.width = map_width
        self.height = map_height
        self.grid = [[0] * map_width for _ in range(map_height)]
        self.biome_grid = None

        {
            "cave": lambda: self._gen_cave(0, map_width),
            "dungeon": lambda: self._gen_dungeon(0, map_width),
            "island": lambda: self._gen_island(0, map_width),
        }.get(biome, lambda: None)()

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts and img2:
            self._spawn_npcs(npc_count, player, frames_dicts)
            self._place_items(img2)

    def generate_multi_biome(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, img2=None, tile_images=None):
        self.biome = biomes[0][0]
        self.bg_color = self.BIOME_BG.get(self.biome, (0, 0, 0))
        self.width = map_width
        self.height = map_height
        self.grid = [[0] * map_width for _ in range(map_height)]
        self.biome_grid = [[None] * map_width for _ in range(map_height)]

        total = sum(w for _, w in biomes)
        strips = []
        offset = 0
        for biome, w in biomes:
            end = offset + int(map_width * w / total)
            strips.append((biome, offset, end))
            offset = end
        if strips:
            strips[-1] = (strips[-1][0], strips[-1][1], map_width)

        for biome, x1, x2 in strips:
            for y in range(map_height):
                for x in range(x1, x2):
                    self.biome_grid[y][x] = biome

        for biome, x1, x2 in strips:
            gen = {
                "cave": self._gen_cave,
                "dungeon": self._gen_dungeon,
                "island": self._gen_island,
            }.get(biome)
            if gen:
                gen(x1, x2)

        for i in range(len(strips) - 1):
            _, x1, x2 = strips[i]
            _, nx1, _ = strips[i + 1]
            mid_x = (x2 + nx1) // 2
            cy = map_height // 2
            for dy in range(-2, 3):
                for dx in range(-1, 2):
                    yy, xx = cy + dy, mid_x + dx
                    if 0 <= yy < map_height and 0 <= xx < map_width:
                        self.grid[yy][xx] = 0

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts and img2:
            self._spawn_npcs(npc_count, player, frames_dicts)
            self._place_items(img2)

    def generate_surface(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, img2=None, tile_images=None):
        self.biome = biomes[0]
        self.bg_color = self.BIOME_BG.get(self.biome, (45, 60, 45))
        self.width = map_width
        self.height = map_height
        self.grid = [[0] * map_width for _ in range(map_height)]
        self.biome_grid = [[None] * map_width for _ in range(map_height)]

        SEA_LEVEL = 0.35
        BEACH_LEVEL = 0.38

        biome_noise = self._octave_noise(map_width, map_height, 2, 40)
        elevation = self._octave_noise(map_width, map_height, 4, 50)

        b_min = min(min(row) for row in biome_noise)
        b_max = max(max(row) for row in biome_noise)
        b_rng = b_max - b_min

        for y in range(map_height):
            for x in range(map_width):
                n = (biome_noise[y][x] - b_min) / b_rng if b_rng > 0 else 0.5
                idx = min(int(n * len(biomes)), len(biomes) - 1)
                biome = biomes[idx]
                self.biome_grid[y][x] = biome

                cfg = self.BIOME_CONFIG.get(biome, {})
                base_h = cfg.get("base_height", 0.5)
                amp_h = cfg.get("height_amp", 0.15)

                elev = base_h + (elevation[y][x] - 0.5) * amp_h * 2
                elev = max(0, min(1, elev))

                if elev < SEA_LEVEL:
                    self.grid[y][x] = 2
                elif elev < BEACH_LEVEL:
                    self.grid[y][x] = 5
                else:
                    self.grid[y][x] = cfg.get("surface", 3)

        for y in range(map_height):
            for x in range(map_width):
                if self.grid[y][x] in (0, 2):
                    continue
                biome = self.biome_grid[y][x]
                cfg = self.BIOME_CONFIG.get(biome, {})
                deco = cfg.get("decoration")
                chance = cfg.get("decoration_chance", 0)
                if deco and random.random() < chance and self.grid[y][x] == cfg.get("surface", 3):
                    self.grid[y][x] = deco

        for y in range(1, map_height - 1):
            for x in range(1, map_width - 1):
                if self.grid[y][x] != 2 and self.grid[y][x] not in (0, 1):
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if self.grid[y + dy][x + dx] == 2:
                                self.grid[y][x] = 5
                                break
                        else:
                            continue
                        break

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts and img2:
            self._spawn_npcs(npc_count, player, frames_dicts)
            self._place_items(img2)

    def generate_island(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, img2=None, tile_images=None):
        self.biome = biomes[0]
        self.bg_color = self.BIOME_BG.get("island", (25, 40, 55))
        self.width = map_width
        self.height = map_height
        self.grid = [[2] * map_width for _ in range(map_height)]
        self.biome_grid = [[None] * map_width for _ in range(map_height)]

        shape_noise = self._octave_noise(map_width, map_height, 3, 25)
        biome_noise = self._octave_noise(map_width, map_height, 2, 40)
        elevation = self._octave_noise(map_width, map_height, 4, 50)

        cx, cy = map_width / 2, map_height / 2
        max_d = math.sqrt(cx ** 2 + cy ** 2)

        ISLAND_THRESHOLD = 0.45

        island_cells = []
        for y in range(map_height):
            for x in range(map_width):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_d
                falloff = 1.0 - dist ** 1.5
                falloff = max(0, min(1, falloff))

                island_h = falloff * (0.5 + shape_noise[y][x] * 0.5)
                if island_h >= ISLAND_THRESHOLD:
                    island_cells.append((x, y, biome_noise[y][x], elevation[y][x]))

        if not island_cells:
            island_cells = [(cx, cy, 0.5, 0.5)]

        b_vals = [c[2] for c in island_cells]
        b_min, b_max = min(b_vals), max(b_vals)
        b_rng = b_max - b_min

        for x, y, bn, ev in island_cells:
            n = (bn - b_min) / b_rng if b_rng > 0 else 0.5
            idx = min(int(n * len(biomes)), len(biomes) - 1)
            biome = biomes[idx]
            self.biome_grid[y][x] = biome

            cfg = self.BIOME_CONFIG.get(biome, {})
            base_h = cfg.get("base_height", 0.5)
            amp_h = cfg.get("height_amp", 0.15)

            elev = base_h + (ev - 0.5) * amp_h * 2
            elev = max(0, min(1, elev))

            self.grid[y][x] = cfg.get("surface", 3)

        for y in range(map_height):
            for x in range(map_width):
                if self.grid[y][x] in (0, 2):
                    continue
                biome = self.biome_grid[y][x]
                cfg = self.BIOME_CONFIG.get(biome, {})
                deco = cfg.get("decoration")
                chance = cfg.get("decoration_chance", 0)
                if deco and random.random() < chance and self.grid[y][x] == cfg.get("surface", 3):
                    self.grid[y][x] = deco

        for y in range(1, map_height - 1):
            for x in range(1, map_width - 1):
                if self.grid[y][x] not in (0, 1, 2):
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if self.grid[y + dy][x + dx] == 2:
                                self.grid[y][x] = 5
                                break
                        else:
                            continue
                        break

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts and img2:
            self._spawn_npcs(npc_count, player, frames_dicts)
            self._place_items(img2)

    def _noise_2d(self, w, h, scale):
        cw = max(2, int(w / scale) + 2)
        ch = max(2, int(h / scale) + 2)
        grid = [[random.random() for _ in range(cw)] for _ in range(ch)]

        result = [[0.0] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                fx = x / scale
                fy = y / scale
                ix = int(fx)
                iy = int(fy)
                frac_x = fx - ix
                frac_y = fy - iy
                ix = min(ix, cw - 2)
                iy = min(iy, ch - 2)
                v00 = grid[iy][ix]
                v10 = grid[iy][ix + 1]
                v01 = grid[iy + 1][ix]
                v11 = grid[iy + 1][ix + 1]
                sx = frac_x * frac_x * (3 - 2 * frac_x)
                sy = frac_y * frac_y * (3 - 2 * frac_y)
                v0 = v00 + (v10 - v00) * sx
                v1 = v01 + (v11 - v01) * sx
                result[y][x] = v0 + (v1 - v0) * sy

        return result

    def _octave_noise(self, w, h, octaves, scale):
        result = [[0.0] * w for _ in range(h)]
        amp = 1.0
        total = 0
        for _ in range(octaves):
            noise = self._noise_2d(w, h, scale)
            for y in range(h):
                for x in range(w):
                    result[y][x] += noise[y][x] * amp
            total += amp
            amp *= 0.5
            scale *= 0.7
        if total > 0:
            for y in range(h):
                for x in range(w):
                    result[y][x] /= total
        return result

    def _gen_cave(self, x1=0, x2=None):
        if x2 is None:
            x2 = self.width
        for y in range(self.height):
            for x in range(x1, x2):
                self.grid[y][x] = 1 if random.random() < 0.35 else 0

        for _ in range(3):
            new = [row[:] for row in self.grid]
            for y in range(1, self.height - 1):
                for x in range(max(1, x1), min(x2, self.width - 1)):
                    walls = sum(
                        1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if (dx or dy) and 0 <= y + dy < self.height and 0 <= x + dx < self.width
                        and self.grid[y + dy][x + dx] == 1
                    )
                    if self.grid[y][x] == 1:
                        new[y][x] = 1 if walls >= 4 else 0
                    else:
                        new[y][x] = 1 if walls >= 5 else 0
            self.grid = new

        for y in range(1, self.height - 1):
            for x in range(max(1, x1), min(x2, self.width - 1)):
                if self.grid[y][x] == 1 and random.random() < 0.06:
                    self.grid[y][x] = 3

        cx = (x1 + x2) // 2
        cy = self.height // 2
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                yy, xx = cy + dy, cx + dx
                if x1 <= xx < x2 and 0 <= yy < self.height:
                    self.grid[yy][xx] = 0

    def _gen_dungeon(self, x1=0, x2=None):
        if x2 is None:
            x2 = self.width
        for y in range(self.height):
            for x in range(x1, x2):
                self.grid[y][x] = 1
        rooms = []

        gap = 3
        base_w, base_h = 5, 5
        strip_w = x2 - x1
        cols = max(2, strip_w // (base_w + gap))
        rows = max(2, self.height // (base_h + gap))

        for gy in range(rows):
            for gx in range(cols):
                rx = x1 + gx * (base_w + gap) + random.randint(0, 1)
                ry = gy * (base_h + gap) + random.randint(0, 1)
                rw = base_w + random.randint(-1, 2)
                rh = base_h + random.randint(-1, 2)
                if rx + rw >= x2 - 1 or ry + rh >= self.height - 1:
                    continue
                rooms.append((rx, ry, rw, rh))
                for y in range(ry, ry + rh):
                    for x in range(rx, rx + rw):
                        self.grid[y][x] = 0

        for rx, ry, rw, rh in rooms:
            for _ in range(random.randint(1, 3)):
                px = rx + random.randint(1, max(1, rw - 2))
                py = ry + random.randint(1, max(1, rh - 2))
                if self.grid[py][px] == 0:
                    self.grid[py][px] = 3

        for y in range(1, self.height - 1):
            for x in range(max(1, x1 + 1), min(x2 - 1, self.width - 1)):
                if self.grid[y][x] == 0 and random.random() < 0.04:
                    if any(self.grid[y + dy][x + dx] == 1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                        self.grid[y][x] = 4

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

    def _gen_island(self, x1=0, x2=None):
        if x2 is None:
            x2 = self.width
        cx, cy = self.width / 2, self.height / 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        h = [[0.0] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(x1, x2):
                h[y][x] = 1.0 - math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_dist + random.uniform(-0.25, 0.25)

        for _ in range(3):
            h2 = [row[:] for row in h]
            for y in range(1, self.height - 1):
                for x in range(max(1, x1), min(x2, self.width - 1)):
                    total = 0
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                total += h[ny][nx]
                    h2[y][x] = total / 9
            h = h2

        for y in range(self.height):
            for x in range(x1, x2):
                self.grid[y][x] = 2 if h[y][x] < 0.35 else 3

        for y in range(2, self.height - 2):
            for x in range(max(2, x1 + 1), min(x2 - 1, self.width - 2)):
                if self.grid[y][x] == 3 and random.random() < 0.06:
                    self.grid[y][x] = 4

    def _build_blocks(self, tile_images=None):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if tile == 0:
                    continue

                biome = self.biome
                if self.biome_grid:
                    biome = self.biome_grid[y][x] or biome

                fallback = self.FALLBACK_COLORS.get(biome, {})
                walkable = self.NON_BLOCKING_TILES.get(biome, set())

                if tile_images and tile in tile_images:
                    cfg = tile_images[tile]
                    if "variants" in cfg:
                        img_x, img_y = random.choice(cfg["variants"])
                    else:
                        img_x = cfg.get("image_x", 0)
                        img_y = cfg.get("image_y", 0)
                    block = Block(
                        x * self.tile_size, y * self.tile_size,
                        self.tile_size, self.tile_size,
                        cfg["bank"],
                        image_x=img_x,
                        image_y=img_y,
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
                    if 0 <= x < self.width and 0 <= y < self.height and self._is_walkable(self.grid[y][x], x, y):
                        return (x * self.tile_size, y * self.tile_size)
        return (cx * self.tile_size, cy * self.tile_size)

    def _is_walkable(self, tile, x=None, y=None):
        if tile == 0:
            return True
        biome = self.biome
        if self.biome_grid and x is not None and y is not None:
            biome = self.biome_grid[y][x] or biome
        walkable = self.NON_BLOCKING_TILES.get(biome, set())
        return tile in walkable

    def _spawn_npcs(self, count, player, frames_dicts):
        spawned = 0
        attempts = 0
        while spawned < count and attempts < 2000:
            attempts += 1
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self._is_walkable(self.grid[y][x], x, y):
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
                if self._is_walkable(self.grid[y][x], x, y):
                    item = cls(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, img)
                    if hasattr(item, "world"):
                        item.world = self.world
                    self.world.add(item)
                    break
