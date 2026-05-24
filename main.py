import pygame
from Engine import engine as e
from Entities.Player import Player
from Entities.World import World
from Entities.Map import Map

e.init(200, 200, title="Game", fps=60, display_scale=4)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
img = e.resources.images[0]
img2 = e.resources.images[1]

world = World()

player = Player(10, 10, 8, 8, img, world=world)
player.speed = 1
world.add(player)

frames_dict = {
    "image_x":4,
    "image_y":0,
    "shadow": (-4, 0),
    "idle_up": (0, 6),
    "idle_down": (0, 7),
    "idle_left": (0, 5),
    "idle_right": (0, 4),
    "walk_up": (0, 2),
    "walk_down": (0, 3),
    "walk_left": (0, 1),
    "walk_right": (0, 0),
    "bank":img2
}
frames_dict2 = {
    "image_x":8,
    "image_y":0,
    "shadow": (-8, 0),
    "idle_up": (0, 6),
    "idle_down": (0, 7),
    "idle_left": (0, 5),
    "idle_right": (0, 4),
    "walk_up": (0, 2),
    "walk_down": (0, 3),
    "walk_left": (0, 1),
    "walk_right": (0, 0),
    "bank":img2
}
# Associe chaque type de tuile à une zone dans une image bank
# tile_images = {
#     1: {"bank": img2, "image_x": 0, "image_y": 5},  # mur cave/dungeon
#     2: {"bank": img2, "image_x": 4, "image_y": 7},  # eau island
# }

game_map = Map(world)
game_map.generate(
    "cave", 50, 50,
    npc_count=8,
    player=player,
    frames_dicts=[frames_dict,frames_dict2],
    img2=img2,
    # tile_images=tile_images,  # décommente pour utiliser les sprites
)
bg_color = game_map.bg_color

cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)
e.active_camera = cam


def update():
    world.update()
    cam.update()
    cam.apply()
    if e.btn(e.KEY_ESCAPE):
        e.quit()


def draw():
    e.cls(bg_color)
    world.draw()

    if cam.flash_alpha > 0:
        surf = pygame.Surface((e.width(), e.height()), pygame.SRCALPHA)
        surf.fill((*cam.flash_color, cam.flash_alpha))
        e.graphics.screen.blit(surf, (0, 0))

    e.camera()


if __name__ == "__main__":
    e.run(update, draw)
