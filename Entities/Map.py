import random
import math
from Entities.Block import Block
from Entities.Npc import Npc
from Entities.Chest import Chest
from Items.Sword import Sword
from Items.Crossbow import Crossbow


class Map:
    # Tuiles par biome :
    #   0 = vide/air (toujours walkable, jamais rendu)
    #   cave        : 1=paroi,      3=eau
    #   dungeon     : 1=mur, 2=sol, 3=eaux usées, 4=caisse, 5=colonne
    #   island      : 2=eau, 3=sable, 4=rocher
    #   plains      : 2=eau, 3=herbe, 4=caillou, 5=sable, 6=bois, 7=arbre
    #   hills       : 2=eau, 3=herbe, 4=caillou, 5=sable, 6=bois, 7=arbre
    #   rocky_plains: 2=eau, 1=pierre, 4=caillou, 5=sable
    #   forest      : 2=eau, 3=herbe, 4=caillou, 5=sable, 6=bois, 7=arbre
    #   desert      : 2=eau (oasis), 5=sable, 4=caillou
    #   mountains   : 2=eau, 1=pierre, 4=caillou, 5=sable

    # Tuile de sol de base pour chaque biome (utilisée comme fond sous les blocs)
    GROUND_TILE = {
        "cave": 1,
        "dungeon": 2,
        "island": 3,
        "plains": 3,
        "hills": 3,
        "rocky_plains": 4,
        "forest": 3,
        "desert": 5,
        "mountains": 1,
    }

    BIOME_BG = {
        "cave":    (20, 18, 25),
        "dungeon": (30, 30, 35),
        "island":  (25, 40, 55),
        "plains":  (45, 60, 45),
        "hills":   (40, 55, 40),
        "rocky_plains": (45, 45, 50),
        "forest":  (35, 55, 35),
        "desert":  (60, 55, 35,0),
        "mountains": (45, 45, 55),
    }

    FALLBACK_COLORS = {
        "cave":    {1: (80, 75, 65), 3: (100, 220, 255)},
        "dungeon": {1: (70, 65, 60), 2: (55, 50, 45), 3: (160, 140, 60), 4: (65, 50, 35), 5: (60, 55, 50),
                    20: (85, 80, 75), 21: (85, 80, 75), 22: (75, 70, 65), 23: (75, 70, 65),
                    24: (120, 105, 90), 25: (120, 105, 90), 26: (120, 105, 90), 27: (120, 105, 90),
                    14: (255, 180, 80)},
        "island":  {2: (10, 55, 85), 3: (181, 174, 145), 4: (70, 65, 60), 14: (255, 180, 80)},
        "plains":  {2: (10, 55, 85), 3: (60, 130, 60), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30), 10: (220, 200, 80), 11: (50, 110, 50), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
        "hills":   {2: (10, 55, 85), 3: (55, 120, 55), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30), 10: (220, 200, 80), 11: (50, 110, 50), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
        "rocky_plains": {2: (10, 55, 85), 1: (100, 100, 100), 4: (120, 115, 110), 5: (200, 180, 120), 10: (220, 200, 80), 11: (60, 100, 60), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
        "forest":  {2: (10, 55, 85), 3: (40, 100, 40), 4: (100, 100, 100), 5: (200, 180, 120), 6: (130, 100, 60), 7: (90, 60, 30), 10: (220, 200, 80), 11: (50, 110, 50), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
        "desert":  {2: (10, 55, 85), 5: (200, 180, 120), 4: (160, 140, 100), 10: (220, 200, 80), 11: (80, 120, 60), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
        "mountains": {2: (10, 55, 85), 1: (140, 140, 150), 4: (120, 115, 110), 5: (200, 180, 120), 10: (220, 200, 80), 11: (60, 100, 60), 12: (200, 120, 160), 13: (70, 140, 60), 14: (255, 180, 80)},
    }

    NON_BLOCKING_TILES = {
        "cave": {3},
        "dungeon": {2, 3, 14},
        "island": {2, 3, 4},
        "plains": {3, 5, 6, 10, 11, 12, 13, 14},
        "hills": {3, 5, 6, 4, 10, 11, 12, 13, 14},
        "rocky_plains": {1, 5, 10, 11, 12, 13, 14},
        "forest": {3, 5, 6, 10, 11, 12, 13, 14},
        "desert": {5, 2, 4, 10, 11, 12, 13, 14},
        "mountains": {5, 10, 11, 12, 13, 14},
    }

    # Tuiles considerees comme "interieur d'une salle" (sol + decoration).
    # Utilise pour l'enveloppe 1-epaisseur des murs.
    ROOM_TILES = frozenset({2, 3, 4, 5})

    # Sous-tuiles pour les murs du dungeon. 12 sprites au total :
    #   - 2 horizontaux : horiz_n (room au S), horiz_s (room au N)
    #   - 2 verticaux   : vert_e (room a l'W), vert_w (room a l'E)
    #   - 4 limite      : outer corners (room des 2 cotes non-mur)
    #   - 4 deviation   : inner corners (room d'un seul cote)
    # Les caps (1 voisin mur), T-junctions (3), cross (4) et single (0)
    # tombent sur le sprite de coin le plus proche.
    WALL_TILES = {
        "horiz_n":     20,  # murs W+E, room au S
        "horiz_s":     21,  # murs W+E, room au N
        "vert_e":      22,  # murs N+S, room a l'W
        "vert_w":      23,  # murs N+S, room a l'E
        "limite_NW":   24,  # murs E+S, room aux S ET E
        "limite_NE":   25,  # murs W+S, room aux S ET W
        "limite_SW":   26,  # murs E+N, room aux N ET E
        "limite_SE":   27,  # murs W+N, room aux N ET W
        "deviation_nw":28,  # murs E+S, room au S OU E (un seul)
        "deviation_ne":29,  # murs W+S, room au S OU W (un seul)
        "deviation_sw":30,  # murs E+N, room au N OU E (un seul)
        "deviation_se":31,  # murs W+N, room au N OU W (un seul)
    }
    WALL_TILE_IDS = frozenset(WALL_TILES.values())

    BIOME_CONFIG = {
    "plains": {
        "surface": 3,
        "decoration": None,
        "decoration_chance": 0.02,
        "decoration_variants": [(10, 3), (11, 2), (13, 1), (14, 1)],
        "base_height": 0.38,
        "height_amp": 0.18,
    },
    "hills": {
        "surface": 3,
        "decoration": 4,
        "decoration_chance": 0.04,
        "decoration_variants": [(10, 2), (11, 3), (13, 1), (14, 1)],
        "base_height": 0.50,
        "height_amp": 0.28,
    },
    "rocky_plains": {
        "surface": 1,
        "decoration": 4,
        "decoration_chance": 0.08,
        "decoration_variants": [(11, 2), (12, 1), (14, 1)],
        "base_height": 0.45,
        "height_amp": 0.18,
    },
    "forest": {
        "surface": 3,
        "decoration": 7,
        "decoration_chance": 0.14,
        "decoration_variants": [(10, 3), (11, 4), (12, 1), (13, 2), (14, 1)],
        "base_height": 0.42,
        "height_amp": 0.22,
    },
    "desert": {
        "surface": 5,
        "decoration": 4,
        "decoration_chance": 0.02,
        "decoration_variants": [(10, 1), (13, 2), (14, 1)],
        "base_height": 0.35,
        "height_amp": 0.10,
    },
    "mountains": {
        "surface": 1,
        "decoration": None,
        "decoration_chance": 0.03,
        "decoration_variants": [(11, 2), (12, 1), (14, 1)],
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
        self.room_tiles = set()

    FILL_TILE = 8

    def _filter_tiles(self, whitelist):
        if whitelist is not None:
            if isinstance(whitelist, int):
                whitelist = (whitelist,)
            for y in range(self.height):
                for x in range(self.width):
                    tile = self.grid[y][x]
                    if tile == 0:
                        continue
                    if tile not in whitelist:
                        self.grid[y][x] = self.FILL_TILE

            for _ in range(6):
                new_grid = [row[:] for row in self.grid]
                fill = self.FILL_TILE
                for y in range(1, self.height - 1):
                    for x in range(1, self.width - 1):
                        if self.grid[y][x] == fill:
                            nz = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                                     if (dx or dy) and self.grid[y + dy][x + dx] != 0
                                     and self.grid[y + dy][x + dx] != fill)
                            if nz >= 5:
                                biome = self.biome
                                if self.biome_grid:
                                    biome = self.biome_grid[y][x] or biome
                                new_grid[y][x] = self.GROUND_TILE.get(biome, 1)
                self.grid = new_grid

    def generate(self, biome, map_width, map_height, npc_count=5, player=None, frames_dicts=None, npc_configs=None, img2=None, item_configs=None, tile_images=None, tile_whitelist=None):
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

        self._filter_tiles(tile_whitelist)
        self._classify_walls()
        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts or npc_configs:
            self._spawn_npcs(npc_count, player, frames_dicts=frames_dicts, npc_configs=npc_configs)
        if img2 or item_configs:
            self._place_items(img=img2, item_configs=item_configs)

    def generate_multi_biome(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, npc_configs=None, img2=None, item_configs=None, tile_images=None, tile_whitelist=None):
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

        self._filter_tiles(tile_whitelist)

        # Colonne de mur 1-epaisseur a la frontiere logique des biomes.
        # Place apres _filter_tiles pour ne pas etre effacee par le filtre.
        for i in range(len(strips) - 1):
            _, x1, x2 = strips[i]
            _, nx1, _ = strips[i + 1]
            wall_x = (x2 + nx1) // 2
            for y in range(map_height):
                if 0 <= wall_x < map_width and self._is_walkable(self.grid[y][wall_x], wall_x, y):
                    self.grid[y][wall_x] = 1

        # Classifie tous les murs (frontieres + sous-types dungeon).
        self._classify_walls()

        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts or npc_configs:
            self._spawn_npcs(npc_count, player, frames_dicts=frames_dicts, npc_configs=npc_configs)
        if img2 or item_configs:
            self._place_items(img=img2, item_configs=item_configs)

    def generate_surface(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, npc_configs=None, img2=None, item_configs=None, tile_images=None, tile_whitelist=None):
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
                chance = cfg.get("decoration_chance", 0)
                if self.grid[y][x] == cfg.get("surface", 3) and random.random() < chance:
                    variants = cfg.get("decoration_variants")
                    if variants:
                        tiles, weights = zip(*variants)
                        self.grid[y][x] = random.choices(tiles, weights=weights, k=1)[0]
                    else:
                        deco = cfg.get("decoration")
                        if deco:
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

        self._filter_tiles(tile_whitelist)
        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts or npc_configs:
            self._spawn_npcs(npc_count, player, frames_dicts=frames_dicts, npc_configs=npc_configs)
        if img2 or item_configs:
            self._place_items(img=img2, item_configs=item_configs)

    def generate_island(self, biomes, map_width, map_height, npc_count=5, player=None, frames_dicts=None, npc_configs=None, img2=None, item_configs=None, tile_images=None, tile_whitelist=None):
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
                chance = cfg.get("decoration_chance", 0)
                if self.grid[y][x] == cfg.get("surface", 3) and random.random() < chance:
                    variants = cfg.get("decoration_variants")
                    if variants:
                        tiles, weights = zip(*variants)
                        self.grid[y][x] = random.choices(tiles, weights=weights, k=1)[0]
                    else:
                        deco = cfg.get("decoration")
                        if deco:
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

        self._filter_tiles(tile_whitelist)
        self._build_blocks(tile_images)

        spawn = self.get_spawn_point()
        if player:
            player.x = spawn[0]
            player.y = spawn[1]

        if frames_dicts or npc_configs:
            self._spawn_npcs(npc_count, player, frames_dicts=frames_dicts, npc_configs=npc_configs)
        if img2 or item_configs:
            self._place_items(img=img2, item_configs=item_configs)

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

    def _flood_find(self, x1, x2, sx, sy):
        if not (x1 <= sx < x2 and 0 <= sy < self.height):
            return set()
        if self.grid[sy][sx] != 0:
            return set()
        visited = set()
        stack = [(sx, sy)]
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (x1 <= x < x2 and 0 <= y < self.height):
                continue
            if self.grid[y][x] != 0:
                continue
            visited.add((x, y))
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                stack.append((x + dx, y + dy))
        return visited

    def _gen_cave(self, x1=0, x2=None):
        if x2 is None:
            x2 = self.width
        for y in range(self.height):
            for x in range(x1, x2):
                self.grid[y][x] = 1 if random.random() < 0.40 else 0

        for _ in range(4):
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

        cx, cy = (x1 + x2) // 2, self.height // 2
        main_area = self._flood_find(x1, x2, cx, cy)
        for y in range(self.height):
            for x in range(x1, x2):
                if self.grid[y][x] == 0 and (x, y) not in main_area:
                    self.grid[y][x] = 1

        for y in range(1, self.height - 1):
            for x in range(max(1, x1), min(x2, self.width - 1)):
                if self.grid[y][x] == 1 and random.random() < 0.06:
                    self.grid[y][x] = 3

        for dy in range(-3, 4):
            for dx in range(-3, 4):
                yy, xx = cy + dy, cx + dx
                if x1 <= xx < x2 and 0 <= yy < self.height:
                    self.grid[yy][xx] = 0

    def _gen_dungeon(self, x1=0, x2=None):
        if x2 is None:
            x2 = self.width
        self.room_tiles = set()

        # Initialiser en vide (0)
        for y in range(self.height):
            for x in range(x1, x2):
                self.grid[y][x] = 0

        gap = 6
        base_w, base_h = 7, 7
        strip_w = x2 - x1
        cols = max(2, strip_w // (base_w + gap))
        rows = max(2, self.height // (base_h + gap))

        # Placer les salles
        rooms = []
        cx_list = []
        cy_list = []
        for gy in range(rows):
            for gx in range(cols):
                rx = x1 + gx * (base_w + gap) + random.randint(0, 1)
                ry = gy * (base_h + gap) + random.randint(0, 1)
                rw = base_w + random.randint(-1, 2)
                rh = base_h + random.randint(-1, 2)
                rx = max(x1 + 1, min(rx, x2 - rw - 2))
                ry = max(1, min(ry, self.height - rh - 2))
                if rw < 3 or rh < 3:
                    continue
                rooms.append((rx, ry, rw, rh))
                cx_list.append(rx + rw // 2)
                cy_list.append(ry + rh // 2)
                for y in range(ry, ry + rh):
                    for x in range(rx, rx + rw):
                        self.grid[y][x] = 2
                        self.room_tiles.add((x, y))

        # Connecter les salles (minimum spanning tree)
        parent = list(range(len(rooms)))
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        def union(u, v):
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[rv] = ru

        edges = []
        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                ax, ay = cx_list[i], cy_list[i]
                bx, by = cx_list[j], cy_list[j]
                dist = abs(ax - bx) + abs(ay - by)
                edges.append((dist, i, j, ax, ay, bx, by))
        edges.sort()

        for dist, i, j, ax, ay, bx, by in edges:
            if find(i) != find(j):
                union(i, j)
                for x in range(min(ax, bx), max(ax, bx) + 1):
                    if x1 <= x < x2 and 0 <= ay < self.height:
                        self.grid[ay][x] = 2
                for y in range(min(ay, by), max(ay, by) + 1):
                    if 0 <= y < self.height and x1 <= bx < x2:
                        self.grid[y][bx] = 2

        # Murs de bordure
        #for y in range(self.height):
        #    for x in range(x1, x2):
        #       if y == 0 or y == self.height - 1 or x == x1 or x == x2 - 1:
        #           self.grid[y][x] = 0

        # Murs fins : tout 0 adjacent à du sol (2) → 1
        for y in range(self.height):
            for x in range(x1, x2):
                if self.grid[y][x] != 0:
                    continue
                if any(
                    0 <= ny < self.height and 0 <= nx < self.width
                    and self.grid[ny][nx] == 2
                    for ny in (y-1, y, y+1) for nx in (x-1, x, x+1)
                    if (ny != y or nx != x)
                ):
                    self.grid[y][x] = 1

        # Points d'eau décoratifs
        placed_loot = set()
        for rx, ry, rw, rh in rooms:
            for _ in range(random.randint(1, 10)):
                px = rx + random.randint(1, max(1, rw - 2))
                py = ry + random.randint(1, max(1, rh - 2))
                if self.grid[py][px] == 2 :#and (px, py) not in placed_loot:
                    self.grid[py][px] = 3
                    placed_loot.add((px, py))

        # Caisses pres des murs
        for y in range(1, self.height - 1):
            for x in range(max(1, x1 + 1), min(x2 - 1, self.width - 1)):
                if self.grid[y][x] == 2 and random.random() < 0.04:
                    if any(self.grid[y + dy][x + dx] == 1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                        self.grid[y][x] = 4

        # Sources de lumiere dans les salles
        for rx, ry, rw, rh in rooms:
            count = random.randint(1, 2)
            for _ in range(count):
                for attempt in range(5):
                    px = rx + random.randint(1, max(1, rw - 2))
                    py = ry + random.randint(1, max(1, rh - 2))
                    if self.grid[py][px] == 2:
                        self.grid[py][px] = 14
                        break

        # Dégager la zone de spawn
        cx, cy = (x1 + x2) // 2, self.height // 2
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                yy, xx = cy + dy, cx + dx
                if x1 <= xx < x2 and 0 <= yy < self.height:
                    self.grid[yy][xx] = 2

        # Dernier passage murs fins : combler les 0 adjacents au nouveau sol
        for y in range(self.height):
            for x in range(x1, x2):
                if self.grid[y][x] != 0:
                    continue
                if any(
                    0 <= ny < self.height and 0 <= nx < self.width
                    and self.grid[ny][nx] == 2
                    for ny in (y-1, y, y+1) for nx in (x-1, x, x+1)
                    if (ny != y or nx != x)
                ):
                    self.grid[y][x] = 1

    def _enclose_with_walls(self, x1, x2):
        h, w = self.height, self.width
        for y in range(h):
            for x in range(x1, x2):
                if self.grid[y][x] in self.ROOM_TILES:
                    continue
                adjacent_room = False
                # 4 directions cardinales
                if y > 0       and self.grid[y - 1][x] in self.ROOM_TILES: adjacent_room = True
                if y < h - 1   and self.grid[y + 1][x] in self.ROOM_TILES: adjacent_room = True
                if x > 0       and self.grid[y][x - 1] in self.ROOM_TILES: adjacent_room = True
                if x < w - 1   and self.grid[y][x + 1] in self.ROOM_TILES: adjacent_room = True
                # 4 diagonales (coins de salle)
                if y > 0       and x > 0     and self.grid[y - 1][x - 1] in self.ROOM_TILES: adjacent_room = True
                if y > 0       and x < w - 1 and self.grid[y - 1][x + 1] in self.ROOM_TILES: adjacent_room = True
                if y < h - 1   and x > 0     and self.grid[y + 1][x - 1] in self.ROOM_TILES: adjacent_room = True
                if y < h - 1   and x < w - 1 and self.grid[y + 1][x + 1] in self.ROOM_TILES: adjacent_room = True
                if adjacent_room:
                    self.grid[y][x] = 1

    def _classify_walls(self):
        """Remplace chaque tuile 1 (mur generique) par un sous-type parmi
        les 12 sprites disponibles. La classification regarde :
          - les 4 voisins cardinaux (murs)
          - la position de la room (tuiles 2,3,4,5) sur les cotes non-mur
        Les cas a 0, 1, 3 ou 4 voisins mur (single, cap, T, cross)
        retombent sur le sprite de coin le plus adapte."""
        h, w = self.height, self.width
        WT = self.WALL_TILES
        new_grid = [row[:] for row in self.grid]
        for y in range(h):
            for x in range(w):
                if self.grid[y][x] != 1:
                    continue
                n  = y > 0     and self.grid[y - 1][x] == 1
                s  = y < h - 1 and self.grid[y + 1][x] == 1
                we = x > 0     and self.grid[y][x - 1] == 1
                e  = x < w - 1 and self.grid[y][x + 1] == 1

                n_room = y > 0     and self.grid[y - 1][x] in self.ROOM_TILES
                s_room = y < h - 1 and self.grid[y + 1][x] in self.ROOM_TILES
                w_room = x > 0     and self.grid[y][x - 1] in self.ROOM_TILES
                e_room = x < w - 1 and self.grid[y][x + 1] in self.ROOM_TILES

                wc = int(n) + int(s) + int(we) + int(e)
                tile_id = WT["limite_NW"]  # fallback

                # Diagonale room (cellule interieure au coin)
                diag_se = y < h-1 and x < w-1 and self.grid[y+1][x+1] in self.ROOM_TILES
                diag_sw = y < h-1 and x > 0   and self.grid[y+1][x-1] in self.ROOM_TILES
                diag_ne = y > 0   and x < w-1 and self.grid[y-1][x+1] in self.ROOM_TILES
                diag_nw = y > 0   and x > 0   and self.grid[y-1][x-1] in self.ROOM_TILES

                if wc == 2:
                    if we and e:
                        tile_id = WT["horiz_s"] if n_room else WT["horiz_n"]
                    elif n and s:
                        tile_id = WT["vert_w"] if e_room else WT["vert_e"]
                    elif n and we:
                        # Murs N+W  → cellule au SE de la room
                        if s_room and e_room:
                            tile_id = WT["limite_SE"]
                        else:
                            tile_id = WT["deviation_se"]
                    elif n and e:
                        # Murs N+E  → cellule au SW de la room
                        if s_room and w_room:
                            tile_id = WT["limite_SW"]
                        else:
                            tile_id = WT["deviation_sw"]
                    elif s and we:
                        # Murs S+W  → cellule au NE de la room
                        if n_room and e_room:
                            tile_id = WT["limite_NE"]
                        else:
                            tile_id = WT["deviation_ne"]
                    elif s and e:
                        # Murs S+E  → cellule au NW de la room
                        if n_room and w_room:
                            tile_id = WT["limite_NW"]
                        else:
                            tile_id = WT["deviation_nw"]
                elif wc == 1:
                    if n or s:
                        tile_id = WT["vert_w"] if e_room else WT["vert_e"]
                    else:
                        tile_id = WT["horiz_s"] if n_room else WT["horiz_n"]
                elif wc == 3:
                    # T-junction : prioriser le segment droit avant le coin
                    if we and e:
                        # Embranchement horizontal (murs W+E + N ou S)
                        if s_room:
                            tile_id = WT["horiz_s"]
                        elif n_room:
                            tile_id = WT["horiz_n"]
                        else:
                            tile_id = WT["horiz_s"] if s else WT["horiz_n"]
                    elif n and s:
                        # Embranchement vertical (murs N+S + W ou E)
                        if e_room:
                            tile_id = WT["vert_w"]
                        elif w_room:
                            tile_id = WT["vert_e"]
                        else:
                            tile_id = WT["vert_w"] if e else WT["vert_e"]
                    else:
                        # Vrai coin 3-murs (L-shape + branche)
                        if not n:  tile_id = WT["limite_SE"]
                        elif not s: tile_id = WT["limite_NE"]
                        elif not we: tile_id = WT["limite_SW"]
                        else:       tile_id = WT["limite_NW"]
                # wc == 0 ou 4 : fallback (limite_NW)

                new_grid[y][x] = tile_id
        self.grid = new_grid

        # Normalise les 12 sous-types en 8 visuels : deviation → outer corner
        dev_to_corner = {
            WT["deviation_nw"]: WT["limite_NW"],
            WT["deviation_ne"]: WT["limite_NE"],
            WT["deviation_sw"]: WT["limite_SW"],
            WT["deviation_se"]: WT["limite_SE"],
        }
        for y in range(self.height):
            for x in range(self.width):
                t = self.grid[y][x]
                if t in dev_to_corner:
                    self.grid[y][x] = dev_to_corner[t]

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

                if tile == self.FILL_TILE:
                    continue

                fallback = self.FALLBACK_COLORS.get(biome, {})
                walkable = self.NON_BLOCKING_TILES.get(biome, set())

                # --- Murs (sous-types 20..35 et mur generique 1) ---
                if tile in self.WALL_TILE_IDS :
                    # Sol sous le mur
                    if tile_images:
                        ground_tile_num = self.GROUND_TILE.get(biome, 1)
                        if ground_tile_num in tile_images:
                            gt_cfg = tile_images[ground_tile_num]
                            if "variants" in gt_cfg:
                                gx, gy = random.choice(gt_cfg["variants"])
                            else:
                                gx = gt_cfg.get("image_x", 0)
                                gy = gt_cfg.get("image_y", 0)
                            ground = Block(
                                x * self.tile_size, y * self.tile_size,
                                self.tile_size, self.tile_size,
                                gt_cfg["bank"],
                                image_x=gx, image_y=gy,
                                color=gt_cfg.get("color"),
                            )
                            ground.blocking = False
                            ground.indestructible = True
                            self.world.add(ground)
                        else:
                            ground_color = fallback.get(ground_tile_num)
                            if ground_color:
                                ground = Block(
                                    x * self.tile_size, y * self.tile_size,
                                    self.tile_size, self.tile_size,
                                    None, color=ground_color,
                                )
                                ground.blocking = False
                                ground.indestructible = True
                                self.world.add(ground)

                    wall_sprite = None
                    if tile_images:
                        ws = tile_images.get("wall_sprites") or {}
                        if tile in ws:
                            wall_sprite = (ws["bank"], ws[tile][0], ws[tile][1])
                    if wall_sprite is not None:
                        bank, img_x, img_y = wall_sprite
                        block = Block(
                            x * self.tile_size, y * self.tile_size,
                            self.tile_size, self.tile_size,
                            bank, image_x=img_x, image_y=img_y,
                        )
                    else:
                        color = fallback.get(tile) or fallback.get(1)
                        if not color:
                            continue
                        block = Block(
                            x * self.tile_size, y * self.tile_size,
                            self.tile_size, self.tile_size,
                            None, color=color,
                        )
                    block.blocking = True
                    block.indestructible = True
                    block.reflective = True
                    self.world.add(block)
                    continue

                # Couche de sol de base (uniquement si tile != sol, pour éviter les doublons)
                if tile_images:
                    ground_tile_num = self.GROUND_TILE.get(biome, 1)
                    if tile != ground_tile_num:
                        if ground_tile_num in tile_images:
                            gt_cfg = tile_images[ground_tile_num]
                            if "variants" in gt_cfg:
                                gx, gy = random.choice(gt_cfg["variants"])
                            else:
                                gx = gt_cfg.get("image_x", 0)
                                gy = gt_cfg.get("image_y", 0)
                            ground = Block(
                                x * self.tile_size, y * self.tile_size,
                                self.tile_size, self.tile_size,
                                gt_cfg["bank"],
                                image_x=gx, image_y=gy,
                                color=gt_cfg.get("color"),
                            )
                            ground.blocking = False
                            ground.indestructible = True
                            ground.is_floor = True
                            self.world.add(ground)
                        else:
                            ground_color = fallback.get(ground_tile_num)
                            if ground_color:
                                ground = Block(
                                    x * self.tile_size, y * self.tile_size,
                                    self.tile_size, self.tile_size,
                                    None, color=ground_color,
                                )
                                ground.blocking = False
                                ground.indestructible = True
                                ground.is_floor = True
                                self.world.add(ground)

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
                    if tile not in (4,):
                        block.is_floor = True
                if (biome == "dungeon" or biome == "cave") and tile == 1:
                    block.indestructible = True
                    block.reflective = True
                if tile in (4,):
                    block.pushable = True
                self.world.add(block)

                # Spawn light source if tile config has dark:True
                if tile_images and tile in tile_images:
                    cfg = tile_images[tile]
                    if cfg.get("dark"):
                        from Entities.Light import Light
                        lx = x * self.tile_size + self.tile_size / 2
                        ly = y * self.tile_size + self.tile_size / 2
                        light = Light(lx, ly, 45, num_rays=16, reflective_bounce=False,
                                      arc_degrees=360, intensity=0.7, color=(255, 200, 120))
                        self.world.lights.append(light)

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
        if tile in self.WALL_TILE_IDS or tile == 1:
            return False
        if tile == 0:
            # Dans un dungeon, le tile 0 represente le vide exterieur :
            # on ne doit pas pouvoir s'y aventurer.
            return self.biome != "dungeon"
        biome = self.biome
        if self.biome_grid and x is not None and y is not None:
            biome = self.biome_grid[y][x] or biome
        walkable = self.NON_BLOCKING_TILES.get(biome, set())
        return tile in walkable

    def _spawn_npcs(self, count, player, frames_dicts=None, npc_configs=None):
        if npc_configs:
            configs = npc_configs
        elif frames_dicts:
            configs = [{"frames_dict": fd} for fd in frames_dicts]
        else:
            return
        spawned = 0
        attempts = 0
        while spawned < count and attempts < 2000:
            attempts += 1
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if self._is_walkable(self.grid[y][x], x, y):
                if self.room_tiles and (x, y) not in self.room_tiles:
                    continue
                cfg = random.choice(configs)
                fd = cfg["frames_dict"]
                npc_kwargs = {k: v for k, v in cfg.items() if k != "frames_dict"}
                self.world.add(Npc(
                    x * self.tile_size, y * self.tile_size,
                    self.tile_size, self.tile_size,
                    target=player, frames_dict=fd,
                    world=self.world, **npc_kwargs,
                ))
                spawned += 1

    def _place_items(self, img=None, item_configs=None):
        if item_configs:
            for cfg in item_configs:
                cls = cfg["cls"]
                bank = cfg["bank"]
                count = cfg.get("count", 1)
                placed_pos = cfg.get("placed_pos")
                if cls is Chest:
                    placed = 0
                    attempts = 0
                    while placed < count and attempts < 2000:
                        attempts += 1
                        if placed_pos is not None and placed == 0:
                            rx, ry = placed_pos
                        else:
                            rx = random.randint(2, self.width - 3)
                            ry = random.randint(2, self.height - 3)
                        if not placed_pos or placed > 0:
                            if not self._is_walkable(self.grid[ry][rx], rx, ry):
                                continue
                        chest = Chest(
                            rx * self.tile_size, ry * self.tile_size,
                            self.tile_size, self.tile_size,
                            bank,
                            image_x=cfg.get("image_x", 0),
                            image_y=cfg.get("image_y", 0),
                            items=cfg.get("items", []),
                            color=cfg.get("color"),
                        )
                        self.world.add(chest)
                        placed += 1
                else:
                    item_kwargs = {k: v for k, v in cfg.items() if k not in ("cls", "bank", "count", "name")}
                    for _ in range(count):
                        for _ in range(500):
                            x = random.randint(2, self.width - 3)
                            y = random.randint(2, self.height - 3)
                            if self._is_walkable(self.grid[y][x], x, y):
                                item = cls(
                                    x * self.tile_size, y * self.tile_size,
                                    self.tile_size, self.tile_size,
                                    bank, name=cfg["name"], **item_kwargs
                                )
                                if hasattr(item, "world"):
                                    item.world = self.world
                                self.world.add(item)
                                break
        elif img:
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
