# Engine — 2D Game Engine (Pygame Backend)

Un moteur de jeu 2D léger, compatible avec l'API Pyxel, construit sur **Pygame**.
Utilise un **écran virtuel** avec mise à l'échelle entière, un système de caméra avec shake et flash, la gestion des entrées (clavier, souris, joystick), l'audio et la gestion de ressources, supprote l'acceleration graphique .

## Utilisation minimale

```python
from Engine import engine as e

e.init(200, 200, title="Mon Jeu", fps=60, display_scale=4)

def update():
    if e.btn(e.KEY_ESCAPE):
        e.quit()

def draw():
    e.cls((30, 30, 40))
    e.rect(10, 10, 20, 20, (255, 0, 0))

e.run(update, draw)
```

## Initialisation

| Fonction | Description |
|---|---|
| `init(width, height, title, fps, display_scale)` | Crée la fenêtre et le moteur |
| `run(update, draw)` | Lance la boucle de jeu |
| `quit()` | Quitte l'application |

- `display_scale` : multiplicateur entier (ex: 4 → fenêtre 800×800 pour virtuel 200×200)
- La `virtual_screen` fait `width × height` pixels logiques, scaled au display

## Entrées clavier

```python
btn(key)    → maintenu ?
btnp(key)   → vient d'être pressé ?
btnr(key)   → vient d'être relâché ?
```

Constantes : `KEY_A`–`KEY_Z`, `KEY_0`–`KEY_9`, `KEY_SPACE`, `KEY_UP`, `KEY_DOWN`,
`KEY_LEFT`, `KEY_RIGHT`, `KEY_ESCAPE`, `KEY_RETURN`, `KEY_LSHIFT`, `KEY_RSHIFT`,
`KEY_LCTRL`, `KEY_RCTRL`, `KEY_LALT`, `KEY_RALT`, `KEY_TAB`, `KEY_BACKSPACE`

## Entrées souris

```python
mouse_x(), mouse_y()            → position en coordonnées logiques
mouse_btn(btn)                  → maintenu ?
mouse_btnp(btn)                 → vient d'être pressé ?
mouse_btnr(btn)                 → vient d'être relâché ?
```

Boutons : `MOUSE_BUTTON_LEFT` (1), `MOUSE_BUTTON_MIDDLE` (2), `MOUSE_BUTTON_RIGHT` (3)

## Dessin (coordonnées monde, affectées par la caméra)

```python
cls(color)                        → remplir l'écran
pset(x, y, color)                 → pixel
pget(x, y)                        → lire un pixel
line(x1, y1, x2, y2, color)       → ligne
rect(x, y, w, h, color)           → rectangle plein
rectb(x, y, w, h, color)          → rectangle vide (1px)
circ(x, y, r, color)              → cercle plein
circb(x, y, r, color)             → cercle vide (1px)
elli(x, y, w, h, color)           → ellipse pleine
ellib(x, y, w, h, color)          → ellipse vide (1px)
tri(x1,y1, x2,y2, x3,y3, color)   → triangle plein
trib(...)                         → triangle vide (1px)
text(x, y, "texte", color)        → texte (police par défaut 16px)
```

### Alpha (RGBA)

Toutes les primitives ci-dessus (sauf `text`) acceptent des couleurs RGBA :
`rect(10, 10, 20, 20, (255, 0, 0, 128))` → blending additif

### Blit d'image

```python
blt(x, y, img, u, v, w, h, colkey=None, rotate=0)
```

- `img` : surface Pygame (ex: chargée via `resources.image()`)
- `u, v, w, h` : région source dans l'image
- `colkey` : couleur de transparence
- `rotate` : rotation en degrés (sens horaire, pivot au centre)

## Caméra

```python
camera(dx, dy)      → applique un décalage à tout le dessin
camera()            → réinitialise à (0, 0)
```

### Camera intelligente (suivi de cible)

```python
cam = e.Camera(target, largeur, hauteur, mouse_influence=0.2, mouse_limit=10)
cam.shake(duration, intensity)    → tremblement
cam.flash(color, alpha, duration) → flash écran
cam.update()                      → calcule le décalage
cam.apply()                       → applique au moteur graphique
```

- La caméra suit `target` (objet avec `.x`, `.y`)
- `mouse_influence` : la souris attire le regard (0.0–1.0)
- `mouse_limit` : décalage max du regard (pixels)
- `_global_mouse_pos` : position souris en coordonnées monde (après `update()`)

## Ressources

```python
resources.image(bank, path, colkey=None)  → charge une image dans bank[index]
resources.sound(bank, path)               → charge un son
resources.music(bank, path)               → enregistre un chemin musique
```

- Les images sont stockées dans `resources.images[bank]`
- Les sons dans `resources.sounds[bank]`

## Audio

```python
audio.play(channel, sound_key, loop=False)   → joue un son
audio.playm(music_key, loop=False)           → joue une musique
audio.stop(channel=None)                     → stop (tout si None)
audio.play_pos(channel)                      → canal actif ?
```

- 8 canaux (0–7) pour les effets sonores
- 1 flux musique via `pygame.mixer.music`

## Clipping

```python
clip(x, y, w, h)    → active le rectangle de clipping
clip()              → désactive
```

## Exemple complet

```python
from Engine import engine as e
from random import randint

e.init(200, 200, "Demo", 60, 4)
img = e.resources.image(0, "sprites.png")

class Player:
    def __init__(self):
        self.x = 100
        self.y = 100

player = Player()
cam = e.Camera(player, e.width(), e.height())

def update():
    if e.btn(e.KEY_LEFT): player.x -= 1
    if e.btn(e.KEY_RIGHT): player.x += 1
    if e.btn(e.KEY_UP): player.y -= 1
    if e.btn(e.KEY_DOWN): player.y += 1
    if e.btn(e.KEY_ESCAPE): e.quit()
    cam.update()
    cam.apply()

def draw():
    e.cls((20, 20, 30))
    e.rect(player.x - 4, player.y - 4, 8, 8, (100, 200, 255))
    e.camera()
    e.text(2, 2, f"FPS: {e.frame_count()}", (255, 255, 255))
    e.circb(e.mouse_x(), e.mouse_y(), 4, (255, 255, 255, 50))

e.run(update, draw)
```
