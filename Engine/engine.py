"""
engine.py – Moteur de jeu 2D avec rendu PyOpenGL (GLFW + Pillow)
API compatible avec le moteur Pygame original.
"""

import importlib.resources as _resources
import math
import pathlib
import random
import sys
from array import array
import ctypes

import glfw
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont

try:
    import miniaudio
    _HAS_AUDIO = True
except Exception:
    miniaudio = None
    _HAS_AUDIO = False

# ----------------------------------------------------------------------
# Constantes de touches (GLFW)
# ----------------------------------------------------------------------
KEY_A = glfw.KEY_A
KEY_B = glfw.KEY_B
KEY_C = glfw.KEY_C
KEY_D = glfw.KEY_D
KEY_E = glfw.KEY_E
KEY_F = glfw.KEY_F
KEY_G = glfw.KEY_G
KEY_H = glfw.KEY_H
KEY_I = glfw.KEY_I
KEY_J = glfw.KEY_J
KEY_K = glfw.KEY_K
KEY_L = glfw.KEY_L
KEY_M = glfw.KEY_M
KEY_N = glfw.KEY_N
KEY_O = glfw.KEY_O
KEY_P = glfw.KEY_P
KEY_Q = glfw.KEY_Q
KEY_R = glfw.KEY_R
KEY_S = glfw.KEY_S
KEY_T = glfw.KEY_T
KEY_U = glfw.KEY_U
KEY_V = glfw.KEY_V
KEY_W = glfw.KEY_W
KEY_X = glfw.KEY_X
KEY_Y = glfw.KEY_Y
KEY_Z = glfw.KEY_Z
KEY_0 = glfw.KEY_0
KEY_1 = glfw.KEY_1
KEY_2 = glfw.KEY_2
KEY_3 = glfw.KEY_3
KEY_4 = glfw.KEY_4
KEY_5 = glfw.KEY_5
KEY_6 = glfw.KEY_6
KEY_7 = glfw.KEY_7
KEY_8 = glfw.KEY_8
KEY_9 = glfw.KEY_9
KEY_SPACE = glfw.KEY_SPACE
KEY_UP = glfw.KEY_UP
KEY_DOWN = glfw.KEY_DOWN
KEY_LEFT = glfw.KEY_LEFT
KEY_RIGHT = glfw.KEY_RIGHT
KEY_ESCAPE = glfw.KEY_ESCAPE
KEY_ENTER = glfw.KEY_ENTER
KEY_RETURN = glfw.KEY_ENTER
KEY_LSHIFT = glfw.KEY_LEFT_SHIFT
KEY_RSHIFT = glfw.KEY_RIGHT_SHIFT
KEY_LCTRL = glfw.KEY_LEFT_CONTROL
KEY_RCTRL = glfw.KEY_RIGHT_CONTROL
KEY_LALT = glfw.KEY_LEFT_ALT
KEY_RALT = glfw.KEY_RIGHT_ALT
KEY_TAB = glfw.KEY_TAB
KEY_BACKSPACE = glfw.KEY_BACKSPACE

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_RIGHT = 2
MOUSE_BUTTON_MIDDLE = 3

# ----------------------------------------------------------------------
# Couleur
# ----------------------------------------------------------------------
def _norm_color(color):
    n = tuple(c / 255.0 for c in color[:3])
    if len(color) == 4:
        return n + (color[3] / 255.0,)
    return n + (1.0,)

def _has_alpha(color):
    return len(color) == 4

# ----------------------------------------------------------------------
# Police
# ----------------------------------------------------------------------
_pixel_font_cache = {}

def _font_path():
    try:
        return str(_resources.files('Engine') / 'fonts' / 'PressStart2P.ttf')
    except Exception:
        return str(pathlib.Path("assests/fonts/PressStart2P.ttf"))

# ----------------------------------------------------------------------
# Image compatible (PIL + cache texture OpenGL)
# ----------------------------------------------------------------------
class _Img:
    __slots__ = ('_pil', '_tex_id', '_tex_up')
    def __init__(self, pil):
        self._pil = pil
        self._tex_id = 0
        self._tex_up = False

    def get_width(self):
        return self._pil.width

    def get_height(self):
        return self._pil.height

    def get_size(self):
        return self._pil.size

    def _ensure_tex(self):
        if not self._tex_up:
            self._tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self._tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            data = self._pil.tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self._pil.width, self._pil.height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, data)
            self._tex_up = True

    def subsurface(self, *args):
        if len(args) == 4:
            u, v, w, h = args
        else:
            u, v, w, h = args[0]
        c = self._pil.crop((u, v, u + w, v + h))
        return _Img(c)

    def set_alpha(self, alpha):
        r, g, b, a = self._pil.split()
        a = a.point(lambda _: alpha)
        self._pil = Image.merge('RGBA', (r, g, b, a))
        self._tex_up = False


# Équivalent Font.render -> _Img
class _FontWrap:
    def __init__(self, pil_font, size):
        self._font = pil_font
        self._size = size

    @property
    def font(self):
        return self._font

    def render(self, s, antialias, color):
        dummy = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        dr = ImageDraw.Draw(dummy)
        bb = dr.textbbox((0, 0), s, font=self._font)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        if tw < 1:
            tw = 1
        if th < 1:
            th = 1
        img = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.text((0, 0), s, font=self._font, fill=color)
        if not antialias:
            # PIL TrueType always anti-aliases; threshold alpha for crisp pixel font
            r, g, b, a = img.split()
            a = a.point(lambda x: 255 if x > 127 else 0)
            img = Image.merge('RGBA', (r, g, b, a))
        return _Img(img)


def default_font(size=6):
    if size not in _pixel_font_cache:
        try:
            pil_font = ImageFont.truetype(_font_path(), size)
        except Exception:
            pil_font = ImageFont.load_default()
        _pixel_font_cache[size] = _FontWrap(pil_font, size)
    return _pixel_font_cache[size]


# ----------------------------------------------------------------------
# ScreenWrapper – émule e.graphics.screen.blit() / fill() / set_at() / get_at()
# ----------------------------------------------------------------------
class _Screen:
    _cleanup_chain = []

    def __init__(self, width, height):
        self._w = width
        self._h = height

    def get_width(self):
        return self._w

    def get_height(self):
        return self._h

    def get_size(self):
        return (self._w, self._h)

    def blit(self, source, dest, area=None, special_flags=0):
        if isinstance(dest, (list, tuple)):
            dx, dy = int(dest[0]), int(dest[1])
        else:
            dx, dy = int(dest.x), int(dest.y)

        if isinstance(source, _Img):
            pil_img = source._pil
        elif isinstance(source, Image.Image):
            pil_img = source
        else:
            w, h = source.get_size()
            data = None
            if hasattr(source, 'tobytes'):
                data = source.tobytes()
            elif hasattr(source, 'get_buffer'):
                data = bytes(source.get_buffer())
            if data is None:
                return
            try:
                pil_img = Image.frombuffer('RGBA', (w, h), data, 'raw', 'RGBA', 0, 1)
            except Exception:
                return

        if area:
            u, v, w, h = area
            pil_img = pil_img.crop((u, v, u + w, v + h))
        w, h = pil_img.size

        tex_id = getattr(pil_img, '_tex_id', None)
        if tex_id is not None:
            tex = tex_id
            glBindTexture(GL_TEXTURE_2D, tex)
        else:
            tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                         pil_img.tobytes())
            pil_img._tex_id = tex

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2i(dx, dy)
        glTexCoord2f(1, 0); glVertex2i(dx + w, dy)
        glTexCoord2f(1, 1); glVertex2i(dx + w, dy + h)
        glTexCoord2f(0, 1); glVertex2i(dx, dy + h)
        glEnd()

    def fill_polygon(self, points, color):
        c = _norm_color(color)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*c)
        glBegin(GL_TRIANGLE_FAN)
        for px, py in points:
            glVertex2i(int(px), int(py))
        glEnd()
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def fill_rect(self, x, y, w, h, color):
        c = _norm_color(color)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*c)
        glBegin(GL_QUADS)
        glVertex2i(x, y)
        glVertex2i(x + w, y)
        glVertex2i(x + w, y + h)
        glVertex2i(x, y + h)
        glEnd()
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def fill(self, color):
        c = _norm_color(color)
        glClearColor(c[0], c[1], c[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def set_at(self, pos, color):
        glDisable(GL_TEXTURE_2D)
        c = _norm_color(color)
        glColor4f(*c)
        glBegin(GL_QUADS)
        glVertex2i(int(pos[0]), int(pos[1]))
        glVertex2i(int(pos[0]) + 1, int(pos[1]))
        glVertex2i(int(pos[0]) + 1, int(pos[1]) + 1)
        glVertex2i(int(pos[0]), int(pos[1]) + 1)
        glEnd()
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)

    def get_at(self, pos):
        data = glReadPixels(int(pos[0]), self._h - int(pos[1]) - 1, 1, 1,
                            GL_RGBA, GL_UNSIGNED_BYTE)
        return (data[0], data[1], data[2], data[3])


# ----------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------
class Input:
    def __init__(self, window):
        self._window = window
        self._keys_pressed = {}
        self._keys_just_pressed = {}
        self._keys_just_released = {}
        self._mouse_pressed = {}
        self._mouse_just_pressed = {}
        self._mouse_just_released = {}
        self._mouse_x = 0
        self._mouse_y = 0
        self._joysticks = []

        glfw.set_key_callback(window, self._key_cb)
        glfw.set_mouse_button_callback(window, self._mouse_cb)
        glfw.set_cursor_pos_callback(window, self._cursor_cb)

    def _key_cb(self, window, key, scancode, action, mods):
        if key < 0:
            return
        if action == glfw.PRESS or action == glfw.REPEAT:
            self._keys_just_pressed[key] = True
            self._keys_pressed[key] = True
        elif action == glfw.RELEASE:
            self._keys_just_released[key] = True
            self._keys_pressed[key] = False

    def _mouse_cb(self, window, button, action, mods):
        b = button + 1
        if action == glfw.PRESS:
            self._mouse_just_pressed[b] = True
            self._mouse_pressed[b] = True
        elif action == glfw.RELEASE:
            self._mouse_just_released[b] = True
            self._mouse_pressed[b] = False

    def _cursor_cb(self, window, x, y):
        self._mouse_x = x
        self._mouse_y = y

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
        mode = glfw.CURSOR_NORMAL if visible else glfw.CURSOR_HIDDEN
        glfw.set_input_mode(self._window, glfw.CURSOR, mode)

    def mouse_btn(self, button):
        return self._mouse_pressed.get(button, False)

    def mouse_btnp(self, button):
        return self._mouse_just_pressed.get(button, False)

    def mouse_btnr(self, button):
        return self._mouse_just_released.get(button, False)


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
            pil = Image.open(img_path).convert('RGBA')
            if colkey:
                data = pil.load()
                for y in range(pil.height):
                    for x in range(pil.width):
                        p = data[x, y]
                        if p[:3] == colkey[:3]:
                            data[x, y] = (0, 0, 0, 0)
            while len(self.images) <= bank:
                self.images.append(None)
            self.images[bank] = _Img(pil)
            return self.images[bank]
        except Exception as e:
            print(f"Erreur chargement image {img_path}: {e}")
            return None

    def sound(self, bank, sound_path):
        if not _HAS_AUDIO:
            print(f"Audio non disponible — son ignoré: {sound_path}")
            return None
        try:
            decoded = miniaudio.decode_file(sound_path)
            self.sounds[bank] = decoded
            return decoded
        except Exception as e:
            print(f"Erreur chargement son {sound_path}: {e}")
            return None

    def music(self, bank, music_path):
        self.musics[bank] = music_path

    def tilemap(self, bank):
        return None


# ----------------------------------------------------------------------
# Audio (via miniaudio)
# ----------------------------------------------------------------------
def _sound_generator(samples, nchannels, fmt, loop, done):
    """Génère des trames PCM. `done` est une liste [bool] mise à True quand le son finit."""
    bytes_per_sample = 2
    if fmt in (miniaudio.SampleFormat.FLOAT32, miniaudio.SampleFormat.SIGNED32):
        bytes_per_sample = 4
    pos = 0
    frames_needed = 1024
    while True:
        avail = (len(samples) - pos) // nchannels
        if avail <= 0:
            if loop:
                pos = 0
                avail = len(samples) // nchannels
            else:
                done[0] = True
                return
        take = min(frames_needed, avail)
        chunk = samples[pos:pos + take * nchannels]
        pos += take * nchannels
        frames_needed = yield bytes(chunk)


class Audio:
    def __init__(self):
        self.sounds = {}
        self.musics = {}
        self._devices = [None] * 8
        self._music_device = None
        self._done_flags = [[False] for _ in range(8)]

    def play(self, ch, s, loop=False):
        if not _HAS_AUDIO or ch >= 8 or s not in self.sounds:
            return
        self.stop(ch)
        sf = self.sounds[s]
        self._done_flags[ch][0] = False
        gen = _sound_generator(sf.samples, sf.nchannels,
                               sf.sample_format, loop,
                               self._done_flags[ch])
        next(gen)
        try:
            dev = miniaudio.PlaybackDevice(
                output_format=sf.sample_format,
                nchannels=sf.nchannels,
                sample_rate=sf.sample_rate,
            )
            dev.start(gen)
            self._devices[ch] = dev
        except Exception as e:
            print(f"Erreur lecture son canal {ch}: {e}")

    def playm(self, m, loop=False):
        if not _HAS_AUDIO or m not in self.musics:
            return
        self._stop_music()
        path = self.musics[m]
        try:
            gen = miniaudio.stream_file(path)
            next(gen)
            dev = miniaudio.PlaybackDevice()
            dev.start(gen)
            self._music_device = dev
        except Exception as e:
            print(f"Erreur lecture musique {m}: {e}")

    def stop(self, ch=None):
        if ch is None:
            for i in range(8):
                self.stop(i)
            self._stop_music()
        elif ch < 8 and self._devices[ch]:
            try:
                self._devices[ch].close()
            except Exception:
                pass
            self._devices[ch] = None
            self._done_flags[ch][0] = True

    def _stop_music(self):
        if self._music_device:
            try:
                self._music_device.close()
            except Exception:
                pass
            self._music_device = None

    def play_pos(self, ch):
        if ch < 8:
            return not self._done_flags[ch][0]
        return False


# ----------------------------------------------------------------------
# Vertex batches (VBO — remplace glBegin/glEnd)
# ----------------------------------------------------------------------
class _FillBatch:
    """Batch de triangles pleins (GL_TRIANGLES) avec VBO."""
    def __init__(self):
        self._vbo = glGenBuffers(1)
        self.clear()

    def clear(self):
        self._data = []
        self._count = 0

    def _push(self, x, y, c):
        self._data.extend((x, y, c[0], c[1], c[2], c[3]))
        self._count += 1

    def quad(self, x, y, w, h, color):
        c = _norm_color(color)
        self._push(x, y, c)
        self._push(x + w, y, c)
        self._push(x, y + h, c)
        self._push(x + w, y, c)
        self._push(x + w, y + h, c)
        self._push(x, y + h, c)

    def triangle(self, x1, y1, x2, y2, x3, y3, color):
        c = _norm_color(color)
        self._push(x1, y1, c)
        self._push(x2, y2, c)
        self._push(x3, y3, c)

    def circ_filled(self, cx, cy, r, color):
        c = _norm_color(color)
        segs = max(8, int(r * 2))
        if segs < 3:
            self._push(cx, cy, c)
            return
        step = 2.0 * math.pi / segs
        for i in range(segs):
            a1 = step * i
            a2 = step * (i + 1)
            self._push(cx, cy, c)
            self._push(cx + r * math.cos(a1), cy + r * math.sin(a1), c)
            self._push(cx + r * math.cos(a2), cy + r * math.sin(a2), c)

    def elli_filled(self, cx, cy, rx, ry, color):
        c = _norm_color(color)
        segs = max(8, int((rx + ry) / 2))
        if segs < 3:
            self._push(cx, cy, c)
            return
        step = 2.0 * math.pi / segs
        for i in range(segs):
            a1 = step * i
            a2 = step * (i + 1)
            self._push(cx, cy, c)
            self._push(cx + rx * math.cos(a1), cy + ry * math.sin(a1), c)
            self._push(cx + rx * math.cos(a2), cy + ry * math.sin(a2), c)

    def flush(self):
        if self._count == 0:
            return
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        arr = array('f', self._data)
        glBufferData(GL_ARRAY_BUFFER, arr.tobytes(), GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        stride = 24
        glVertexPointer(2, GL_FLOAT, stride, ctypes.c_void_p(0))
        glColorPointer(4, GL_FLOAT, stride, ctypes.c_void_p(8))
        glDisable(GL_TEXTURE_2D)
        glDrawArrays(GL_TRIANGLES, 0, self._count)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.clear()

    def destroy(self):
        glDeleteBuffers(1, [self._vbo])


class _LineBatch:
    """Batch de lignes (GL_LINES) avec VBO."""
    def __init__(self):
        self._vbo = glGenBuffers(1)
        self.clear()

    def clear(self):
        self._data = []
        self._count = 0

    def _push(self, x, y, c):
        self._data.extend((x, y, c[0], c[1], c[2], c[3]))
        self._count += 1

    def line(self, x1, y1, x2, y2, color):
        c = _norm_color(color)
        self._push(x1, y1, c)
        self._push(x2, y2, c)

    def loop(self, points, color):
        c = _norm_color(color)
        n = len(points)
        if n < 2:
            return
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            self._push(x1, y1, c)
            self._push(x2, y2, c)

    def flush(self, line_width=1.0):
        if self._count == 0:
            return
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        arr = array('f', self._data)
        glBufferData(GL_ARRAY_BUFFER, arr.tobytes(), GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        stride = 24
        glVertexPointer(2, GL_FLOAT, stride, ctypes.c_void_p(0))
        glColorPointer(4, GL_FLOAT, stride, ctypes.c_void_p(8))
        glDisable(GL_TEXTURE_2D)
        if line_width > 1.0:
            glLineWidth(line_width)
        glDrawArrays(GL_LINES, 0, self._count)
        if line_width > 1.0:
            glLineWidth(1.0)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.clear()

    def destroy(self):
        glDeleteBuffers(1, [self._vbo])


# ----------------------------------------------------------------------
# Font Atlas (bitmap — plus de PIL dans la boucle de rendu)
# ----------------------------------------------------------------------
class _FontAtlas:
    def __init__(self, font_wrap):
        self._font = font_wrap
        self._glyphs = {}
        self._tex_id = 0
        if font_wrap is not None:
            self._build()

    def _build(self):
        dummy = Image.new('RGBA', (1, 1))
        dr = ImageDraw.Draw(dummy)
        bb = dr.textbbox((0, 0), 'W', font=self._font.font)
        cell_w = max(1, bb[2] - bb[0] + 1)
        cell_h = max(1, bb[3] - bb[1])

        cols = 16
        pad = 1
        atlas_w = cols * (cell_w + pad) + pad
        atlas_h = 6 * (cell_h + pad) + pad
        atlas = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(atlas)

        for i, code in enumerate(range(32, 128)):
            col = i % cols
            row = i // cols
            gx = pad + col * (cell_w + pad)
            gy = pad + row * (cell_h + pad)
            ch = chr(code)
            bb2 = dr.textbbox((0, 0), ch, font=self._font.font)
            cw = max(1, bb2[2] - bb2[0])
            dr.text((gx, gy), ch, font=self._font.font, fill=(255, 255, 255))
            self._glyphs[code] = (gx, gy, cw, cell_h)

        r, g, b, a = atlas.split()
        a = a.point(lambda x: 255 if x > 127 else 0)
        atlas = Image.merge('RGBA', (r, g, b, a))

        self._tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, atlas.width, atlas.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, atlas.tobytes())
        self._tex_w = atlas_w
        self._tex_h = atlas_h

    def render(self, dx, dy, s, color):
        glBindTexture(GL_TEXTURE_2D, self._tex_id)
        x = dx
        for ch in s:
            code = ord(ch)
            if code < 32 or code > 126:
                code = 32
            gx, gy, gw, gh = self._glyphs.get(code, self._glyphs[32])
            u1 = gx / self._tex_w
            v1 = gy / self._tex_h
            u2 = (gx + gw) / self._tex_w
            v2 = (gy + gh) / self._tex_h
            glBegin(GL_QUADS)
            glColor4f(*color)
            glTexCoord2f(u1, v1); glVertex2f(x, dy)
            glTexCoord2f(u2, v1); glVertex2f(x + gw, dy)
            glTexCoord2f(u2, v2); glVertex2f(x + gw, dy + gh)
            glTexCoord2f(u1, v2); glVertex2f(x, dy + gh)
            glEnd()
            x += gw


# ----------------------------------------------------------------------
# Graphiques (OpenGL + VBO + Font Atlas)
# ----------------------------------------------------------------------
class Graphics:
    def __init__(self, width, height, display_scale, pixel_art=True):
        self._w = width
        self._h = height
        self._scale = display_scale
        self._pixel_art = pixel_art
        self._camera_x = 0
        self._camera_y = 0
        self._clip_rect = None
        self._font_wrap = None
        self._font_atlas = None
        self._tex_cache = {}
        self._colkey_cache = {}

        self._fill = _FillBatch()
        self._lines = _LineBatch()
        self.screen = _Screen(width, height)

        glViewport(0, 0, width * display_scale, height * display_scale)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glReadBuffer(GL_BACK)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    # --- Aide texture ---
    def _upload_tex(self, pil_img):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, pil_img.width, pil_img.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, pil_img.tobytes())
        return tex

    def _tex_of(self, img):
        if isinstance(img, _Img):
            img._ensure_tex()
            return img._tex_id, img._pil.width, img._pil.height
        if isinstance(img, Image.Image):
            tid = self._tex_cache.get(id(img))
            if tid is None:
                tid = self._upload_tex(img)
                self._tex_cache[id(img)] = tid
            return tid, img.width, img.height
        return 0, 0, 0

    # --- Primitives (accumulées dans les batches) ---
    def _r(self, *args):
        if not self._pixel_art:
            return args if len(args) > 1 else args[0]
        return tuple(round(v) for v in args)

    def cls(self, color):
        self.flush()
        c = _norm_color(color)
        glClearColor(c[0], c[1], c[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def pset(self, x, y, color):
        x, y = self._r(x, y)
        self._fill.quad(x + self._camera_x, y + self._camera_y, 1, 1, color)

    def pget(self, x, y):
        x += self._camera_x
        y += self._camera_y
        if 0 <= x < self._w and 0 <= y < self._h:
            data = glReadPixels(int(x), int(self._h * self._scale - y - 1),
                                1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
            return (data[0], data[1], data[2], data[3])
        return (0, 0, 0, 0)

    def line(self, x1, y1, x2, y2, color):
        x1, y1, x2, y2 = self._r(x1, y1, x2, y2)
        self._lines.line(x1 + self._camera_x, y1 + self._camera_y,
                         x2 + self._camera_x, y2 + self._camera_y, color)

    def rect(self, x, y, w, h, color):
        x, y, w, h = self._r(x, y, w, h)
        self._fill.quad(x + self._camera_x, y + self._camera_y, w, h, color)

    def rectb(self, x, y, w, h, color):
        x, y, w, h = self._r(x, y, w, h)
        cx, cy = x + self._camera_x, y + self._camera_y
        self._lines.loop([(cx, cy), (cx + w, cy),
                          (cx + w, cy + h), (cx, cy + h)], color)

    def circ(self, x, y, r, color):
        x, y, r = self._r(x, y, r)
        self._fill.circ_filled(x + self._camera_x, y + self._camera_y, r, color)

    def circb(self, x, y, r, color):
        x, y, r = self._r(x, y, r)
        cx, cy = x + self._camera_x, y + self._camera_y
        segs = max(8, int(r * 2))
        pts = [(cx + r * math.cos(2 * math.pi * i / segs),
                cy + r * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
        self._lines.loop(pts, color)

    def elli(self, x, y, w, h, color):
        x, y, w, h = self._r(x, y, w, h)
        cx, cy = x + self._camera_x + w / 2, y + self._camera_y + h / 2
        self._fill.elli_filled(cx, cy, w / 2, h / 2, color)

    def ellib(self, x, y, w, h, color):
        x, y, w, h = self._r(x, y, w, h)
        cx, cy = x + self._camera_x + w / 2, y + self._camera_y + h / 2
        segs = max(8, int((w + h) / 2))
        pts = [(cx + w / 2 * math.cos(2 * math.pi * i / segs),
                cy + h / 2 * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
        self._lines.loop(pts, color)

    def tri(self, x1, y1, x2, y2, x3, y3, color):
        x1, y1, x2, y2, x3, y3 = self._r(x1, y1, x2, y2, x3, y3)
        self._fill.triangle(x1 + self._camera_x, y1 + self._camera_y,
                            x2 + self._camera_x, y2 + self._camera_y,
                            x3 + self._camera_x, y3 + self._camera_y, color)

    def trib(self, x1, y1, x2, y2, x3, y3, color):
        x1, y1, x2, y2, x3, y3 = self._r(x1, y1, x2, y2, x3, y3)
        cx1, cy1 = x1 + self._camera_x, y1 + self._camera_y
        cx2, cy2 = x2 + self._camera_x, y2 + self._camera_y
        cx3, cy3 = x3 + self._camera_x, y3 + self._camera_y
        self._lines.loop([(cx1, cy1), (cx2, cy2), (cx3, cy3)], color)

    # --- Texte (Font Atlas) ---
    def text(self, x, y, s, color, font=None):
        if font is None:
            if self._font_atlas is None:
                self._font_wrap = default_font(6)
                self._font_atlas = _FontAtlas(self._font_wrap)
            atlas = self._font_atlas
        elif isinstance(font, _FontWrap) and hasattr(font, '_atlas'):
            atlas = font._atlas
        else:
            self._legacy_text(x, y, s, color, font)
            return
        self._fill.flush()
        self._lines.flush()
        c = _norm_color(color)
        glEnable(GL_TEXTURE_2D)
        atlas.render(x + self._camera_x, y + self._camera_y, s, c)
        glColor4f(1, 1, 1, 1)

    def _legacy_text(self, x, y, s, color, font):
        dummy = Image.new('RGBA', (1, 1))
        dr = ImageDraw.Draw(dummy)
        bb = dr.textbbox((0, 0), s, font=font.font)
        tw = max(1, bb[2] - bb[0])
        th = max(1, bb[3] - bb[1])
        img = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        dr.text((0, 0), s, font=font.font, fill=color)
        r, g, b, a = img.split()
        a = a.point(lambda x: 255 if x > 127 else 0)
        img = Image.merge('RGBA', (r, g, b, a))
        tex = self._upload_tex(img)
        dx = x + self._camera_x
        dy = y + self._camera_y
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(dx, dy)
        glTexCoord2f(1, 0); glVertex2f(dx + tw, dy)
        glTexCoord2f(1, 1); glVertex2f(dx + tw, dy + th)
        glTexCoord2f(0, 1); glVertex2f(dx, dy + th)
        glEnd()
        glDeleteTextures(1, [tex])

    # --- Blit ---
    def blt(self, x, y, img, u, v, w, h, colkey=None, rotate=0):
        dx = round(x + self._camera_x)
        dy = round(y + self._camera_y)

        if rotate != 0:
            if isinstance(img, _Img):
                pil_src = img._pil
            elif isinstance(img, Image.Image):
                pil_src = img
            else:
                return
            sub = pil_src.crop((u, v, u + w, v + h))
            sub = sub.rotate(rotate, expand=True, resample=Image.NEAREST)
            if colkey is not None:
                if isinstance(colkey, int):
                    ck = (colkey & 0xFF, (colkey >> 8) & 0xFF, (colkey >> 16) & 0xFF)
                else:
                    ck = tuple(colkey[:3])
                data = sub.load()
                for py in range(sub.height):
                    for px in range(sub.width):
                        p = data[px, py]
                        if isinstance(p, int):
                            match = (p & 0xFF, (p >> 8) & 0xFF, (p >> 16) & 0xFF) == ck
                        else:
                            match = p[:3] == ck
                        if match:
                            data[px, py] = (0, 0, 0, 0)
            self._fill.flush()
            self._lines.flush()
            tex_id = self._upload_tex(sub)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glEnable(GL_TEXTURE_2D)
            sw, sh = sub.size
            cx = dx + w / 2
            cy = dy + h / 2
            sx = cx - sw / 2
            sy = cy - sh / 2
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(sx, sy)
            glTexCoord2f(1, 0); glVertex2f(sx + sw, sy)
            glTexCoord2f(1, 1); glVertex2f(sx + sw, sy + sh)
            glTexCoord2f(0, 1); glVertex2f(sx, sy + sh)
            glEnd()
            glDeleteTextures(1, [tex_id])
            return

        if colkey is not None and isinstance(img, _Img):
            if isinstance(colkey, int):
                ck = (colkey & 0xFF, (colkey >> 8) & 0xFF, (colkey >> 16) & 0xFF)
            else:
                ck = tuple(colkey[:3])
            key = (id(img), u, v, w, h, ck)
            tid = self._colkey_cache.get(key)
            if tid is None:
                sub = img._pil.crop((u, v, u + w, v + h))
                data = sub.load()
                for py in range(h):
                    for px in range(w):
                        p = data[px, py]
                        if isinstance(p, int):
                            match = (p & 0xFF, (p >> 8) & 0xFF, (p >> 16) & 0xFF) == ck
                        else:
                            match = p[:3] == ck
                        if match:
                            data[px, py] = (0, 0, 0, 0)
                tid = self._upload_tex(sub)
                self._colkey_cache[key] = tid
            tex_id = tid
            tu1 = tv1 = 0
            tu2 = tv2 = 1
        else:
            tex_id, iw, ih = self._tex_of(img)
            tu1 = u / iw if iw > 0 else 0
            tv1 = v / ih if ih > 0 else 0
            tu2 = (u + w) / iw if iw > 0 else 1
            tv2 = (v + h) / ih if ih > 0 else 1

        self._fill.flush()
        self._lines.flush()
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(tu1, tv1); glVertex2f(dx, dy)
        glTexCoord2f(tu2, tv1); glVertex2f(dx + w, dy)
        glTexCoord2f(tu2, tv2); glVertex2f(dx + w, dy + h)
        glTexCoord2f(tu1, tv2); glVertex2f(dx, dy + h)
        glEnd()

    def bltm(self, x, y, tm, u, v, w, h, colkey=None):
        pass

    def clip(self, x=None, y=None, w=None, h=None):
        if x is None:
            glDisable(GL_SCISSOR_TEST)
            self._clip_rect = None
        else:
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(x), int(self._h * self._scale - (y + h)),
                      int(w), int(h))
            self._clip_rect = (x, y, w, h)

    def camera(self, x=None, y=None):
        if x is None:
            self._camera_x = 0
            self._camera_y = 0
        else:
            if self._pixel_art:
                x, y = self._r(x, y)
            self._camera_x = x
            self._camera_y = y

    def flush(self):
        lw = self._scale if self._pixel_art else 1.0
        self._fill.flush()
        self._lines.flush(lw)
        glColor4f(1, 1, 1, 1)

    def pal(self, col1=None, col2=None):
        pass

    def dither(self, alpha):
        pass


# ----------------------------------------------------------------------
# Caméra
# ----------------------------------------------------------------------
def lerp(a,b,t):
    return a+t*(b-a)
class Camera:
    def __init__(self, target, screen_width, screen_height,
                 mouse_influence=0.2, mouse_limit=10):
        self.target = target
        self.width = screen_width
        self.height = screen_height
        self.mouse_influence = mouse_influence
        self.mouse_limit = mouse_limit
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.flash_duration = 0
        self.cam_x = 0
        self.cam_y = 0

    def shake(self, duration, intensity):
        self.shake_duration = duration
        self.shake_intensity = intensity

    def flash(self, color, alpha, duration):
        self.flash_color = color
        self.flash_alpha = alpha
        self.flash_duration = duration

    def update(self):
        global _global_mouse_pos
        if self.flash_alpha > 0:
            self.flash_duration -= 1
            if self.flash_duration <= 0:
                self.flash_alpha = max(0, self.flash_alpha - 8)

        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration % 5 == 0:
                self.shake_intensity = max(0, self.shake_intensity - 1)
        else:
            self.shake_intensity = 0

        if self.shake_intensity > 0:
            self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        mx = mouse_x()
        my = mouse_y()
        _global_mouse_pos = (mx - self.cam_x, my - self.cam_y)
        cx = self.width / 2
        cy = self.height / 2
        dx = (mx - cx) * self.mouse_influence
        dy = (my - cy) * self.mouse_influence
        dx = max(-self.mouse_limit, min(self.mouse_limit, dx))
        dy = max(-self.mouse_limit, min(self.mouse_limit, dy))
        tsx = cx - dx
        tsy = cy - dy
        self.cam_x = lerp(self.cam_x,tsx-self.target.x,0.1)+self.shake_offset_x
        self.cam_y = lerp(self.cam_y,tsy-self.target.y,0.1)+self.shake_offset_y
        #self.cam_x = tsx - self.target.x + self.shake_offset_x 
        #self.cam_y = tsy - self.target.y + self.shake_offset_y

    def apply(self):
        
        camera(self.cam_x, self.cam_y)


# ----------------------------------------------------------------------
# Application principale
# ----------------------------------------------------------------------
class App:
    def __init__(self, width, height, title, fps, display_scale, pixel_art=True):
        if not glfw.init():
            raise RuntimeError("Échec glfw.init()")

        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        glfw.window_hint(glfw.SCALE_TO_MONITOR, glfw.TRUE)

        self.width = width
        self.height = height
        self.display_scale = display_scale
        self.fps = fps
        self.frame_count = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.running = False

        win_w = width * display_scale
        win_h = height * display_scale
        self._window = glfw.create_window(int(win_w), int(win_h), title, None, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Échec création fenêtre GLFW")

        glfw.make_context_current(self._window)
        # VSync désactivé par défaut (compatible headless / tout environnement)
        glfw.swap_interval(0)

        self.input = Input(self._window)
        self.graphics = Graphics(width, height, display_scale, pixel_art)
        self.audio = Audio()
        self.resources = Resources()
        self.audio.sounds = self.resources.sounds
        self.audio.musics = self.resources.musics

    def run(self, update, draw):
        self.running = True
        clock = glfw.get_time()
        target_dt = 1.0 / self.fps

        while self.running and not glfw.window_should_close(self._window):
            now = glfw.get_time()
            dt = now - clock
            clock = now

            glfw.poll_events()

            # Mouse position en coordonnées logiques
            mx, my = glfw.get_cursor_pos(self._window)
            self.mouse_x = mx / self.display_scale
            self.mouse_y = my / self.display_scale

            # Flash overlay
            g = self.graphics
            if g.screen and hasattr(self, '_flash') and self._flash_alpha > 0:
                pass  # flash géré via entité
            update()
            draw()
            """try:
                update()
                draw()
            except Exception as err:
                import traceback
                traceback.print_exc()
                self.running = False"""

            self.input.update()
            self.graphics.flush()
            glfw.swap_buffers(self._window)
            self.frame_count += 1

            # Attente pour respecter le FPS
            elapsed = glfw.get_time() - now
            sleep = target_dt - elapsed
            if sleep > 0:
                import time
                time.sleep(sleep)

        self.quit()

    def quit(self):
        self.running = False
        glfw.terminate()
        sys.exit()


# ----------------------------------------------------------------------
# Interface globale
# ----------------------------------------------------------------------
_app = None
_width = 256
_height = 256
_global_mouse_pos = (0, 0)
active_camera = None

graphics = Graphics(256, 256, 1)
input = Input(None) if False else None  # placeholder
resources = Resources()
audio = Audio()


def init(width, height, title="Pyxel Compat", fps=30, display_scale=1, pixel_art=True):
    global _app, _width, _height, graphics, input, resources, audio
    _width = width
    _height = height
    _app = App(width, height, title, fps, display_scale, pixel_art)
    graphics = _app.graphics
    input = _app.input
    resources = _app.resources
    audio = _app.audio


def run(update, draw):
    if not _app:
        raise RuntimeError("Appel e.init() d'abord")
    _app.run(update, draw)


def quit():
    if _app:
        _app.quit()


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
def mouse_btn(button):
    return input.mouse_btn(button) if input else False

def mouse_btnp(button):
    return input.mouse_btnp(button) if input else False

def mouse_btnr(button):
    return input.mouse_btnr(button) if input else False

def btn(key):
    return input.btn(key) if input else False

def btnp(key, hold=0, period=0):
    return input.btnp(key, hold, period) if input else False

def btnr(key):
    return input.btnr(key) if input else False
