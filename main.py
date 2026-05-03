import Entities
from Engine import engine as e
from Entities.Player import Player
from Entities.Items import Item
import random as rnd

e.init(120, 120, title="Game", fps=60, display_scale=4)
e.resources.image(0, "./assests/images/feuille1.png")
img = e.resources.images[0] if len(e.resources.images) > 0 else None

player = Player(10, 10, 8, 8, img)
player.speed = 1
s = Item(10,10,8,8,img,player)
player.current_item = s
# Création de la caméra
cam = e.Camera(player, e.width(), e.height(), mouse_influence=0.2, mouse_limit=10)
def update():
    # Déclenchement du shake avec la touche Espace
    if e.btnp(e.KEY_SPACE):
        cam.shake(20, 4)

    # Mise à jour du joueur
    player.update()
    # Mise à jour et application de la caméra
    cam.update()
    cam.apply()
    
    if e.btn(e.KEY_Q) or e.btn(e.KEY_ESCAPE):
        e.quit()

def draw():
    e.cls((250, 250, 250))
    player.draw()
    # Interface fixe (hors caméra)
    e.camera()

e.run(update, draw)