"""Mini démo : blit des assets avec animation du joueur (moteur OpenGL)."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from Engine import engine as e

ASSETS = os.path.join(os.path.dirname(__file__), '..', 'assests', 'images')
SHEET1 = os.path.join(ASSETS, 'feuille1.png')
STUFF = os.path.join(ASSETS, 'stuff.png')
TILE = 8

e.init(200, 200, 'GL Blit Demo', fps=15, display_scale=3)

sheet1 = e.resources.image(0, SHEET1)
stuff = e.resources.image(1, STUFF)

if sheet1 is None or stuff is None:
    print("ERREUR: chargement images", file=sys.stderr)
    e.quit()

# Coordonnées tiles (idem jeu original)
POTION_TILE = (3 * TILE, 9 * TILE)
SWORD_TILE = (0 * TILE, 9 * TILE)
BOW_TILE = (1 * TILE, 9 * TILE)

# Joueur : image_x=4, image_y=0, walk_right row=0
PLAYER_BASE = (4 * TILE, 0 * TILE)
SHADOW_TILE = ((4 + 4) * TILE, 0 * TILE)

def update():
    pass

frame = 0

def draw():
    global frame
    frame += 1

    e.cls((32, 32, 48))

    # Damier d'arrière-plan
    for gy in range(25):
        for gx in range(25):
            dx = gx * TILE
            dy = gy * TILE
            c = (60, 70, 50) if (gx + gy) % 2 == 0 else (50, 60, 40)
            e.rect(dx, dy, TILE, TILE, c)

    # Objets au sol
    e.blt(10, 10, stuff, *POTION_TILE, TILE, TILE)
    e.blt(60, 10, stuff, *SWORD_TILE, TILE, TILE)
    e.blt(110, 10, stuff, *BOW_TILE, TILE, TILE)

    # Animation du joueur (4 frames, cycle toutes les 5 ticks)
    anim = (frame // 5) % 4
    px, py = PLAYER_BASE
    src_x = px + anim * TILE

    # Ombre
    e.blt(92, 93, sheet1, *SHADOW_TILE, TILE, TILE)

    # Joueur en walk right
    e.blt(92, 92, sheet1, src_x, py, TILE, TILE)

    # Texte
    e.text(2, 2, f'Frame {frame}', (255, 255, 160))
    e.text(2, 190, 'GL Engine - Feuille1', (160, 160, 200))

e.run(update, draw)
