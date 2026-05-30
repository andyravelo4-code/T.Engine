import pygame
from Engine import engine as e
from Entities.Player import Player
from Entities.World import World
from Entities.Map import Map
from Entities.Inventory import Inventory
from Items.Sword import Sword
from Items.Crossbow import Crossbow
from Items.Consumable import Consumable

MAP_MODE = "island"     # "single" (dungeon/cave/island), "island" (noise+biomes), "surface" (noise+biomes), "multi" (stripes)
MAP_BIOME = "dungeon"   # used when MAP_MODE is "single"
MAP_BIOMES = [ "desert"]  # used when MAP_MODE is island/surface/multi (or list of (biome,weight) for multi)

e.init(200, 200, title="Game", fps=60, display_scale=5)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
sheet1 = e.resources.images[0]
stuff = e.resources.images[1]
world = World()

player = Player(10, 10, 8, 8, sheet1, world=world)
player.speed = 1
world.add(player)

frames_dict = {
    "image_x":4, "image_y":0, "shadow": (-4, 0),
    "idle_up": (0, 6), "idle_down": (0, 7),
    "idle_left": (0, 5), "idle_right": (0, 4),
    "walk_up": (0, 2), "walk_down": (0, 3),
    "walk_left": (0, 1), "walk_right": (0, 0),
    "bank":stuff,
}
frames_dict2 = {
    "image_x":8, "image_y":0, "shadow": (-8, 0),
    "idle_up": (0, 6), "idle_down": (0, 7),
    "idle_left": (0, 5), "idle_right": (0, 4),
    "walk_up": (0, 2), "walk_down": (0, 3),
    "walk_left": (0, 1), "walk_right": (0, 0),
    "bank":stuff,
}

game_map = Map(world)
if MAP_MODE == "single":
    game_map.generate(
        MAP_BIOME, 20, 20,
        npc_count=8, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.6, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.4, "detection_radius": 90, "punch_damage": 8, "punch_cooldown": 50},
        ],
        item_configs=[
            {"cls": Sword, "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow, "bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            {"cls": Consumable, "bank": None, "name": "Potion", "heal_amount": 15, "dropped_pos": (0, 0), "count": 4},
        ],
    )
elif MAP_MODE == "island":
    game_map.generate_island(
        MAP_BIOMES, 20, 20,
        npc_count=4, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.6, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.4, "detection_radius": 20, "punch_damage": 8, "punch_cooldown": 50},
        ],
        item_configs=[
            {"cls": Sword,"name":"excalibour", "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow,"name":"crossbrow", "bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            {"cls": Consumable,"name":"wisky", "bank": stuff, "heal_amount": 15, "dropped_pos": (1, 0), "count": 3},
            {"cls": Consumable,"name":"pomme", "bank": stuff, "heal_amount": 15, "dropped_pos": (2, 0), "count": 2}
        ],
    )
elif MAP_MODE == "surface":
    game_map.generate_surface(
        MAP_BIOMES, 40, 30,
        npc_count=8, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.6, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.4, "detection_radius": 90, "punch_damage": 8, "punch_cooldown": 50},
        ],
        item_configs=[
            {"cls": Sword, "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow, "bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            {"cls": Consumable, "bank": None, "name": "Potion", "heal_amount": 15, "dropped_pos": (0, 0), "count": 4},
        ],
    )
elif MAP_MODE == "multi":
    game_map.generate_multi_biome(
        MAP_BIOMES, 40, 30,
        npc_count=8, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.6, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.4, "detection_radius": 30, "punch_damage": 8, "punch_cooldown": 50},
        ],
        item_configs=[
            {"cls": Sword, "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow, "bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            {"cls": Consumable, "bank": None, "name": "Potion", "heal_amount": 15, "dropped_pos": (0, 0), "count": 4},
        ],
    )
bg_color = game_map.bg_color

cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)
e.active_camera = cam
inventory = Inventory(player)


def update():
    if not inventory.open:
        world.update()
        cam.update()
    cam.apply()

    if e.btnp(e.KEY_I):
        inventory.toggle()

    if not inventory.open:
        if e.btn(e.KEY_ESCAPE):
            e.quit()
        return

    inventory.update()


def draw():
    e.cls(bg_color)
    world.draw()

    if cam.flash_alpha > 0:
        surf = pygame.Surface((e.width(), e.height()), pygame.SRCALPHA)
        surf.fill((*cam.flash_color, cam.flash_alpha))
        e.graphics.screen.blit(surf, (0, 0))

    e.camera()

    inventory.draw()

    if inventory.drag_item and inventory.drag_qty > 0:
        pass
    else:
        e.circb(e.mouse_x(), e.mouse_y(), 4, (255, 255, 255, 50))


if __name__ == "__main__":
    e.run(update, draw)
