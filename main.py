from Engine import engine as e
from Entities.Player import Player
from Entities.Sword import Sword
from Entities.Crossbow import Crossbow
from Entities.World import World
import random as rnd

e.init(120, 120, title="Game", fps=60, display_scale=4)
e.resources.image(0, "./assests/images/feuille1.png")
e.resources.image(1, "./assests/images/stuff.png")
img = e.resources.images[0] 
img2 = e.resources.images[1]

# Initialisation du monde
world = World()

player = Player(10, 10, 8, 8, img)
player.speed = 1

# Création d'items au sol
sword = Sword(40, 40, 8, 8, img2)
crossbow = Crossbow(80, 40, 8, 8, img2, world=world)

world.add(sword)
world.add(crossbow)

# Création de la caméra
cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)

def update():
    # Mise à jour du joueur et du monde
    player.update(world)
    world.update()

    # Mise à jour et application de la caméra
    cam.update()
    cam.apply()
    
    if e.btn(e.KEY_ESCAPE):
        e.quit()

def draw():
    e.cls((112, 198, 169))

    # Dessin du monde et du joueur
    world.draw()
    player.draw()

    # Interface fixe (hors caméra)
    e.camera()

e.run(update, draw)