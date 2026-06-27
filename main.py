import sys
from Engine import engine as e
from Entities.Player import Player
from Entities.World import World
from Entities.Map import Map
from Entities.Inventory import Inventory
from Items.Sword import Sword
from Items.Crossbow import Crossbow
from Items.Consumable import Consumable
from Entities.Chest import Chest
from Entities.Light import Light

MAP_MODE = "single"
MAP_BIOME = "cave"
MAP_BIOMES = [ "desert","island","hills"]  # used when MAP_MODE is island/surface/multi (or list of (biome,weight) for multi)

e.init(300, 200, title="Game", fps=60, display_scale=4, pixel_art=True)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
e.resources.image(2, "./assests/images/Tileset_Wall_Stone_8x8.png")
e.resources.image(3, "./assests/images/floor.png")
sheet1 = e.resources.images[0]
stuff = e.resources.images[1]
walls_ts = e.resources.images[2]
floor = e.resources.images[3]
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
frames_dict3 = {
    "image_x":12, "image_y":0, "shadow": (-12, 0),
    "idle_up": (0, 6), "idle_down": (0, 7),
    "idle_left": (0, 5), "idle_right": (0, 4),
    "walk_up": (0, 2), "walk_down": (0, 3),
    "walk_left": (0, 1), "walk_right": (0, 0),
    "bank":stuff,
}
game_map = Map(world)
world.map = game_map
if MAP_MODE == "single":
    game_map.generate(
        MAP_BIOME,15, 15,
        npc_count=2, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.6, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.4, "detection_radius": 90, "punch_damage": 8, "punch_cooldown": 50},
        ],
        item_configs=[
            {"cls": Sword, "bank": stuff, "name": "Sword", "damage": 30, "dropped_pos": (5, 9), "count": 2 , "held_pos":(4,9) },
            {"cls": Crossbow, "bank": stuff, "name": "Crossbow", "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            
            {"cls": Chest, "bank": stuff, "image_x": 0, "image_y": 5, "placed_pos": (2, 10), "count": 1,}
        ],
        tile_images={
            "wall_sprites": {
                "bank": walls_ts,
                20: (1, 0), 21: (1, 2),
                22: (2, 1), 23: (0, 1),
                24: (0, 0), 25: (2, 0),
                26: (0, 2), 27: (2, 2),
            },
            4 : {"bank":stuff,"image_x":1,"image_y":5},
            3 : {"bank":stuff,"variants":[(1,4),(2,4),(0,4), (0,3),(1,3),(3,5),(3,4)]+[(i,2) for i in range(3)]},
            #2 : {"bank":floor,"variants":[(9,2)]},
        },
        tile_whitelist=(1,2,3,5,4,10,11,12,13)
    )
elif MAP_MODE == "island":
    game_map.generate_island(
        MAP_BIOMES, 20, 20,
        npc_count=6, player=player,
        npc_configs=[
            {"frames_dict": frames_dict, "max_health": 80, "speed": 0.5, "punch_damage": 4, "punch_cooldown": 40},
            {"frames_dict": frames_dict2, "max_health": 150, "speed": 0.5, "detection_radius": 40, "punch_damage": 8, "punch_cooldown": 50},
            {"frames_dict": frames_dict3, "aggressive": False, "max_health": 50, "speed": 0.3},
        ],
        item_configs=[
            {"cls": Sword,"name":"excalibour", "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow,"name":"crossbrow", "bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
            {"cls": Consumable,"name":"wisky", "bank": stuff, "heal_amount": 15, "dropped_pos": (1, 0), "count": 3},
            {"cls": Consumable,"name":"pomme", "bank": stuff, "heal_amount": 15, "dropped_pos": (2, 0), "count": 2},
            {"cls": Chest, "bank": stuff, "image_x": 0, "image_y": 5, "placed_pos": (5, 10), "count": 1,
             "items": [
                 {"cls": Sword, "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "name": "Excalibour"},
                 {"cls": Consumable, "bank": stuff, "name": "Potion", "heal_amount": 20, "dropped_pos": (2, 0)},
             ]},
        ],
        tile_images={
            4:{"bank":stuff,"variants":[(1,4),(2,4),(0,4), (0,3),(1,3),(3,5),(3,4)]+[(i,2) for i in range(3)]},
            #5:{"bank":rev , "variants":[(6,1),(3,1)]}
        },
        
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
            {"cls": Sword,"name":"", "bank": stuff, "damage": 30, "dropped_pos": (3, 9), "count": 2},
            {"cls": Crossbow, "name":"","bank": stuff, "damage": 15, "dropped_pos": (0, 9), "fire_timer": 10, "count": 1},
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

from Entities.Light import Light
torch = Light(0, 0, 80, num_rays=32, reflective_bounce=True, arc_degrees=360, color=(249,194,43))
#world.lights.append(torch)


def update():
    if not inventory.open:
        world.update()
        cam.update()
    cam.apply()

    if e.btnp(e.KEY_I):
        inventory.toggle()
    #torch.x,torch.y = player.x+4,player.y+player.h/2#e._global_mouse_pos
    if not inventory.open:
        if e.btn(e.KEY_ESCAPE):
            e.quit()
        return

    inventory.update()


def draw():
    e.cls(bg_color)
    world.draw()

    if cam.flash_alpha > 0:
        e.graphics.screen.fill_rect(0, 0, e.width(), e.height(),
            (*cam.flash_color, cam.flash_alpha))

    e.camera()

    inventory.draw()

    if inventory.drag_item and inventory.drag_qty > 0:
        pass
    else:
        e.circb(e.mouse_x(), e.mouse_y(), 4, (255, 255, 255, 150))


if __name__ == "__main__":
    e.run(update, draw)
