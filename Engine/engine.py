"""
engine.py – Moteur de jeu compatible Pyxel utilisant Pygame
Sans limitation de palette ni de résolution.
À placer dans le même dossier que votre script principal.
"""

import pygame
import sys
import random

# ----------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------
class Input:
    def __init__(self):
        self._keys_pressed = {}
        self._keys_just_pressed = {}
        self._keys_just_released = {}
        self._mouse_pressed = {}
        self._mouse_just_pressed = {}
        self._mouse_just_released = {}
        self._joysticks = []
        self._init_joysticks()

    def _init_joysticks(self):
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self._joysticks.append(joy)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._keys_just_pressed[event.key] = True
            self._keys_pressed[event.key] = True
        elif event.type == pygame.KEYUP:
            self._keys_just_released[event.key] = True
            self._keys_pressed[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_just_pressed[event.button] = True
            self._mouse_pressed[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_just_released[event.button] = True
            self._mouse_pressed[event.button] = False

    def update(self):
        self._keys_just_pressed.clear()
        self._keys_just_released.clear()
        self._mouse_just_pressed.clear()
        self._mouse_just_released.clear()

    def btn(self, key):
        return self._keys_pressed.get(key, False)

    def btnp(self, key, hold=0, period=0):
        return self._keys_just_pressed.get(key, False)

    def btnr(self, key):
        return self._keys_just_released.get(key, False)

    def mouse(self, visible=True):
        pygame.mouse.set_visible(visible)

    def mouse_btn(self, button):
        return self._mouse_pressed.get(button, False)

    def mouse_btnp(self, button):
        return self._mouse_just_pressed.get(button, False)

    def mouse_btnr(self, button):
        return self._mouse_just_released.get(button, False)

    def joy(self, joy_id, button):
        if joy_id < len(self._joysticks):
            return self._joysticks[joy_id].get_button(button)
        return False

    def joy_axis(self, joy_id, axis):
        if joy_id < len(self._joysticks):
            return self._joysticks[joy_id].get_axis(axis)
        return 0.0


# ----------------------------------------------------------------------
# Ressources
# ----------------------------------------------------------------------
class Resources:
    def __init__(self):
        self.images = []
        self.sounds = {}
        self.musics = {}
        self.tilemaps = []

    def load(self, filename):
        raise NotImplementedError("Chargement .pyxres non implémenté")

    def image(self, bank, img_path, colkey=None):
        try:
            img = pygame.image.load(img_path).convert_alpha()
            if colkey:
                img.set_colorkey(colkey)
            while len(self.images) <= bank:
                self.images.append(None)
            self.images[bank] = img
            return img
        except pygame.error as e:
            print(f"Erreur chargement image {img_path} : {e}")
            return None

    def sound(self, bank, sound_path):
        try:
            sound = pygame.mixer.Sound(sound_path)
            self.sounds[bank] = sound
            return sound
        except pygame.error as e:
            print(f"Erreur chargement son {sound_path} : {e}")
            return None

    def music(self, bank, music_path):
        self.musics[bank] = music_path

    def tilemap(self, bank):
        return None  # non implémenté


# ----------------------------------------------------------------------
# Audio
# ----------------------------------------------------------------------
class Audio:
    def __init__(self):
        pygame.mixer.init()
        self.channels = [pygame.mixer.Channel(i) for i in range(8)]
        self.sounds = {}
        self.musics = {}

    def play(self, ch, s, loop=False):
        if ch < len(self.channels) and s in self.sounds:
            self.channels[ch].play(self.sounds[s], loops=-1 if loop else 0)

    def playm(self, m, loop=False):
        if m in self.musics:
            pygame.mixer.music.load(self.musics[m])
            pygame.mixer.music.play(-1 if loop else 0)

    def stop(self, ch=None):
        if ch is None:
            pygame.mixer.stop()
        elif ch < len(self.channels):
            self.channels[ch].stop()

    def play_pos(self, ch):
        if ch < len(self.channels):
            return self.channels[ch].get_busy()
        return False


# ----------------------------------------------------------------------
# Graphiques
# ----------------------------------------------------------------------
class Graphics:
    def __init__(self, screen=None):
        if screen:
            self.screen = screen
        self._clip_rect = None
        self._camera_x = 0
        self._camera_y = 0

    def cls(self, color):
        self.screen.fill(color)

    def pset(self, x, y, color):
        if self._clip_rect and not self._clip_rect.collidepoint(x, y):
            return
        x += self._camera_x
        y += self._camera_y
        if 0 <= x < self.screen.get_width() and 0 <= y < self.screen.get_height():
            self.screen.set_at((x, y), color)

    def pget(self, x, y):
        x += self._camera_x
        y += self._camera_y
        if 0 <= x < self.screen.get_width() and 0 <= y < self.screen.get_height():
            return self.screen.get_at((x, y))
        return (0, 0, 0, 0)

    def line(self, x1, y1, x2, y2, color):
        pygame.draw.line(
            self.screen,
            color,
            (x1 + self._camera_x, y1 + self._camera_y),
            (x2 + self._camera_x, y2 + self._camera_y),
        )

    def rect(self, x, y, w, h, color):
        r = pygame.Rect(x + self._camera_x, y + self._camera_y, w, h)
        if self._clip_rect:
            r = r.clip(self._clip_rect)
        pygame.draw.rect(self.screen, color, r)

    def rectb(self, x, y, w, h, color):
        r = pygame.Rect(x + self._camera_x, y + self._camera_y, w, h)
        if self._clip_rect:
            r = r.clip(self._clip_rect)
        pygame.draw.rect(self.screen, color, r, 1)

    def circ(self, x, y, r, color):
        pygame.draw.circle(
            self.screen, color, (x + self._camera_x, y + self._camera_y), r
        )

    def circb(self, x, y, r, color):
        pygame.draw.circle(
            self.screen, color, (x + self._camera_x, y + self._camera_y), r, 1
        )

    def elli(self, x, y, w, h, color):
        rect = pygame.Rect(x + self._camera_x, y + self._camera_y, w, h)
        pygame.draw.ellipse(self.screen, color, rect)

    def ellib(self, x, y, w, h, color):
        rect = pygame.Rect(x + self._camera_x, y + self._camera_y, w, h)
        pygame.draw.ellipse(self.screen, color, rect, 1)

    def tri(self, x1, y1, x2, y2, x3, y3, color):
        points = [
            (x1 + self._camera_x, y1 + self._camera_y),
            (x2 + self._camera_x, y2 + self._camera_y),
            (x3 + self._camera_x, y3 + self._camera_y),
        ]
        pygame.draw.polygon(self.screen, color, points)

    def trib(self, x1, y1, x2, y2, x3, y3, color):
        points = [
            (x1 + self._camera_x, y1 + self._camera_y),
            (x2 + self._camera_x, y2 + self._camera_y),
            (x3 + self._camera_x, y3 + self._camera_y),
        ]
        pygame.draw.polygon(self.screen, color, points, 1)

    def text(self, x, y, s, color, font=None):
        font = font or pygame.font.Font(None, 16)
        surf = font.render(s, True, color)
        self.screen.blit(surf, (x + self._camera_x, y + self._camera_y))

    def blt(self, x, y, img, u, v, w, h, colkey=None, rotate=0):
        """
        Dessine une portion d'image avec rotation optionnelle.
        Si rotate != 0, l'image tourne autour de son centre.
        (x, y) correspond alors au coin supérieur gauche de la zone source
        (le centre reste identique qu'il y ait rotation ou non).
        """
        # Extraction de la zone source
        sub = img.subsurface((u, v, w, h))

        if rotate != 0:
            # Rotation de la subsurface
            sub = pygame.transform.rotate(sub, rotate)
            if colkey is not None:
                sub.set_colorkey(colkey)

            # Calcul du centre de la zone source AVANT rotation
            cx = x + w / 2 + self._camera_x
            cy = y + h / 2 + self._camera_y

            # Positionnement de la subsurface tournée par rapport à son centre
            rect = sub.get_rect(center=(cx, cy))
            self.screen.blit(sub, rect.topleft)
        else:
            # Comportement original, sans rotation
            if colkey is not None:
                sub.set_colorkey(colkey)
            self.screen.blit(sub, (x + self._camera_x, y + self._camera_y))

    def bltm(self, x, y, tm, u, v, w, h, colkey=None):
        pass  # non implémenté

    def clip(self, x=None, y=None, w=None, h=None):
        if x is None:
            self._clip_rect = None
        else:
            self._clip_rect = pygame.Rect(x, y, w, h)

    def camera(self, x=None, y=None):
        if x is None:
            self._camera_x = 0
            self._camera_y = 0
        else:
            self._camera_x = x
            self._camera_y = y

    def pal(self, col1=None, col2=None):
        pass

    def dither(self, alpha):
        pass



class Camera:
    """Caméra réutilisable avec suivi de cible, offset souris et tremblement."""
    def __init__(self, target, screen_width, screen_height, mouse_influence=0.2, mouse_limit=10):
        self.target = target                # objet avec .x et .y
        self.width = screen_width
        self.height = screen_height
        self.mouse_influence = mouse_influence  # sensibilité du regard (0..1)
        self.mouse_limit = mouse_limit          # amplitude max en pixels

        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    def shake(self, duration, intensity):
        """Déclenche un tremblement d'écran."""
        self.shake_duration = duration
        self.shake_intensity = intensity

    def update(self):
        # --- Gestion du shake ---
        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration % 5 == 0:
                self.shake_intensity = max(0, self.shake_intensity - 1)
        if self.shake_intensity > 0:
            self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        # --- Offset souris ---
        mx = mouse_x()   # fonction globale de engine
        my = mouse_y()
        center_x = self.width / 2
        center_y = self.height / 2

        # Décalage proportionnel à la distance de la souris au centre
        dx = (mx - center_x) * self.mouse_influence
        dy = (my - center_y) * self.mouse_influence
        # Limitation
        dx = max(-self.mouse_limit, min(self.mouse_limit, dx))
        dy = max(-self.mouse_limit, min(self.mouse_limit, dy))

        # Position écran souhaitée pour la cible
        target_screen_x = center_x - dx
        target_screen_y = center_y - dy

        # Calcul du décalage caméra à appliquer
        self.cam_x = target_screen_x - self.target.x + self.shake_offset_x
        self.cam_y = target_screen_y - self.target.y + self.shake_offset_y
    def apply(self):
        """Applique la caméra calculée."""
        camera(self.cam_x, self.cam_y)    # fonction globale définie dans engine
# ----------------------------------------------------------------------
# Application principale
# ----------------------------------------------------------------------
class App:
    def __init__(self, width, height, title, fps, display_scale):
        pygame.init()
        self.width = width
        self.height = height
        self.display_scale = display_scale
        self.screen = pygame.display.set_mode(
            (width * display_scale, height * display_scale)
        )
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = False
        self.frame_count = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.virtual_screen = pygame.Surface((width, height))
        self.input = Input()
        self.graphics = Graphics(self.virtual_screen)
        self.audio = Audio()
        self.resources = Resources()

    def run(self, update, draw):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.input.handle_event(event)

            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            self.mouse_x //= self.display_scale
            self.mouse_y //= self.display_scale

            update()
            draw()

            self.input.update()

            scaled = pygame.transform.scale(
                self.virtual_screen,
                (self.width * self.display_scale, self.height * self.display_scale),
            )
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()
            self.frame_count += 1
            self.clock.tick(self.fps)

        self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()


# ----------------------------------------------------------------------
# Interface globale (simule l'API de Pyxel)
# ----------------------------------------------------------------------
_app = None
_width = 256
_height = 256

# Modules publics (remplis après init)
graphics = Graphics()
input = Input()
resources = Resources()
audio = Audio()


def init(width, height, title="Pyxel Compat", fps=30, display_scale=1):
    global _app, _width, _height, graphics, input, resources, audio
    _width = width
    _height = height
    _app = App(width, height, title, fps, display_scale)
    graphics = _app.graphics
    input = _app.input
    resources = _app.resources
    audio = _app.audio


def run(update, draw):
    if not _app:
        raise RuntimeError("Appel px.init() d'abord")
    _app.run(update, draw)


def quit():
    if _app:
        _app.quit()


# Propriétés globales

def width():
    return _width


def height():
    return _height


def frame_count():
    return _app.frame_count if _app else 0


def mouse_x():
    return _app.mouse_x if _app else 0


def mouse_y():
    return _app.mouse_y if _app else 0


# Délégation graphique
def cls(color):
    graphics.cls(color)


def pset(x, y, color):
    graphics.pset(x, y, color)


def pget(x, y):
    return graphics.pget(x, y)


def line(x1, y1, x2, y2, color):
    graphics.line(x1, y1, x2, y2, color)


def rect(x, y, w, h, color):
    graphics.rect(x, y, w, h, color)


def rectb(x, y, w, h, color):
    graphics.rectb(x, y, w, h, color)


def circ(x, y, r, color):
    graphics.circ(x, y, r, color)


def circb(x, y, r, color):
    graphics.circb(x, y, r, color)


def elli(x, y, w, h, color):
    graphics.elli(x, y, w, h, color)


def ellib(x, y, w, h, color):
    graphics.ellib(x, y, w, h, color)


def tri(x1, y1, x2, y2, x3, y3, color):
    graphics.tri(x1, y1, x2, y2, x3, y3, color)


def trib(x1, y1, x2, y2, x3, y3, color):
    graphics.trib(x1, y1, x2, y2, x3, y3, color)


def text(x, y, s, color, font=None):
    graphics.text(x, y, s, color, font)


def blt(x, y, img, u, v, w, h, colkey=None, rotate=0):
    graphics.blt(x, y, img, u, v, w, h, colkey, rotate)


def bltm(x, y, tm, u, v, w, h, colkey=None):
    graphics.bltm(x, y, tm, u, v, w, h, colkey)


def clip(x=None, y=None, w=None, h=None):
    graphics.clip(x, y, w, h)


def camera(x=None, y=None):
    graphics.camera(x, y)


def pal(col1=None, col2=None):
    graphics.pal(col1, col2)


def dither(alpha):
    graphics.dither(alpha)


# Délégation entrée
def btn(key):
    return input.btn(key) if input else False


def btnp(key, hold=0, period=0):
    return input.btnp(key, hold, period) if input else False


def btnr(key):
    return input.btnr(key) if input else False


# Constantes de touches (pygame)
KEY_A = pygame.K_a
KEY_B = pygame.K_b
KEY_C = pygame.K_c
KEY_D = pygame.K_d
KEY_E = pygame.K_e
KEY_F = pygame.K_f
KEY_G = pygame.K_g
KEY_H = pygame.K_h
KEY_I = pygame.K_i
KEY_J = pygame.K_j
KEY_K = pygame.K_k
KEY_L = pygame.K_l
KEY_M = pygame.K_m
KEY_N = pygame.K_n
KEY_O = pygame.K_o
KEY_P = pygame.K_p
KEY_Q = pygame.K_q
KEY_R = pygame.K_r
KEY_S = pygame.K_s
KEY_T = pygame.K_t
KEY_U = pygame.K_u
KEY_V = pygame.K_v
KEY_W = pygame.K_w
KEY_X = pygame.K_x
KEY_Y = pygame.K_y
KEY_Z = pygame.K_z
KEY_0 = pygame.K_0
KEY_1 = pygame.K_1
KEY_2 = pygame.K_2
KEY_3 = pygame.K_3
KEY_4 = pygame.K_4
KEY_5 = pygame.K_5
KEY_6 = pygame.K_6
KEY_7 = pygame.K_7
KEY_8 = pygame.K_8
KEY_9 = pygame.K_9
KEY_SPACE = pygame.K_SPACE
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_ESCAPE = pygame.K_ESCAPE
KEY_RETURN = pygame.K_RETURN
KEY_LSHIFT = pygame.K_LSHIFT
KEY_RSHIFT = pygame.K_RSHIFT
KEY_LCTRL = pygame.K_LCTRL
KEY_RCTRL = pygame.K_RCTRL
KEY_LALT = pygame.K_LALT
KEY_RALT = pygame.K_RALT
KEY_TAB = pygame.K_TAB
KEY_BACKSPACE = pygame.K_BACKSPACE