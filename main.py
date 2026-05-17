from Engine import engine as e
from Entities.Crossbow import Crossbow
from Entities.Npc import Npc
from Entities.Player import Player
from Entities.Sword import Sword
from Entities.World import World
from Entities.Block import Block

e.init(200, 200, title="Game", fps=65, display_scale=4)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
img = e.resources.images[0]
img2 = e.resources.images[1]
bg_color = (112, 198, 169)
# Initialisation du monde
world = World()

player = Player(10, 10, 8, 8, img, world=world)
player.speed = 1
world.add(player)

# Création d'items au sol
sword = Sword(40, 40, 8, 8, img2)
crossbow = Crossbow(80, 40, 8, 8, img2, world=world)

world.add(sword)
world.add(crossbow)


# Ajout d'obstacles
world.add(Block(32, 32, 8, 8, img2, 2, 8))
world.add(Block(40, 32, 8, 8, img2, 1, 8))
world.add(Block(48, 32, 8, 8, img2, 2, 8))
world.add(Block(32, 40, 8, 8, img2, 1, 8))
world.add(Block(32, 48, 8, 8, img2, 2, 8))

# Ajout du NPC
frames_dict = {
    "idle_up": 6,
    "idle_down": 7,
    "idle_left": 5,
    "idle_right": 4,
    "walk_up": 2,
    "walk_down": 3,
    "walk_left": 1,
    "walk_right": 0,
}
npc = Npc(80, 80, 8, 8, img, target=player, frames_dict=frames_dict, world=world)
world.add(npc)


# Création de la caméra
cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)
e.active_camera = cam


def outline(bg_color):
    for y in range(0, 121):
        for x in range(0, 121):
            if e.pget(x + 1, y) != bg_color and e.pget(x, y) == bg_color:
                e.pset(x, y, (255, 255, 255))
        for x in range(121, 0, -1):
            if e.pget(x - 1, y) != bg_color and e.pget(x, y) == bg_color:
                e.pset(x, y, (255, 255, 255))
    for x in range(0, 121):
        for y in range(121, 0, -1):
            if e.pget(x, y - 1) != bg_color and e.pget(x, y) == bg_color:
                e.pset(x, y, (255, 255, 255))
        for y in range(0, 121):
            if e.pget(x, y + 1) != bg_color and e.pget(x, y) == bg_color:
                e.pset(x, y, (255, 255, 255))


def update():
    # Mise à jour du monde
    world.update()

    # Mise à jour et application de la caméra
    cam.update()
    cam.apply()
    if e.btn(e.KEY_ESCAPE):
        e.quit()


def draw():
    e.cls(bg_color)

    # Dessin du monde (qui inclut maintenant le joueur)
    world.draw()

    # Interface fixe (hors caméra)
    e.camera()
    # outline(bg_color)


e.run(update, draw)
