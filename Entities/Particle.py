import math
import random
from Engine import engine as e

GRAVITY = 0.08
GROUND_Y = None  # set per-world if needed

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=1, gravity=True, bounce=True):
        self.x = x
        self.y = y
        self.w = size
        self.h = size
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.bounce = bounce

    def update(self):
        # Gravity
        if self.gravity:
            self.vy += GRAVITY

        self.x += self.vx
        self.y += self.vy

        # Bounce off ground
        if self.bounce and GROUND_Y is not None and self.y + self.size >= GROUND_Y:
            self.y = GROUND_Y - self.size
            self.vy *= -0.3
            self.vx *= 0.85
            if abs(self.vy) < 0.3:
                self.vy = 0

        # Friction
        self.vx *= 0.96
        self.vy *= 0.96

        if abs(self.vx) < 0.01:
            self.vx = 0
        if abs(self.vy) < 0.01:
            self.vy = 0

        self.lifetime -= 1

    def draw(self):
        if self.lifetime <= 0:
            return

        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if len(self.color) == 4:
            draw_color = (self.color[0], self.color[1], self.color[2], min(alpha, self.color[3]))
        else:
            draw_color = (self.color[0], self.color[1], self.color[2], alpha)

        sz = self.size
        if sz <= 1:
            e.pset(int(self.x), int(self.y), draw_color)
        else:
            e.elli(int(self.x), int(self.y), sz, sz, draw_color)


def spawn_blood(x, y, world, amount=15):
    """for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 3.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.5
        r = random.randint(160, 255)
        g = random.randint(0, 40)
        b = random.randint(0, 20)
        color = (r, g, b, random.randint(180, 255))
        lifetime = random.randint(20, 35)
        p = Particle(x, y, vx, vy, color, lifetime, size=1, gravity=True, bounce=True)
        world.add(p)"""

    # Splatter near ground
    for _ in range(amount // 2):
        px = x + random.uniform(-4, 4)
        py = y + random.uniform(0, 4)
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-0.3, 0)
        color = (random.randint(120, 180), 0, 0, random.randint(100, 180))
        p = Particle(px, py, vx, vy, color, random.randint(20, 308), size=2, gravity=False, bounce=True)
        world.add(p)


def spawn_dust(x, y, world, amount=6):
    for _ in range(amount):
        angle = random.uniform(-math.pi, 0)
        speed = random.uniform(0.2, 1.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.2
        val = random.randint(90, 160)
        color = (val, val - 10, val - 20, random.randint(80, 180))
        lifetime = random.randint(12, 24)
        p = Particle(x + random.uniform(-2, 2), y, vx, vy, color, lifetime, size=1, gravity=True, bounce=False)
        world.add(p)


def spawn_hit(x, y, world, amount=10):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        r, g = 255, random.randint(200, 255)
        b = random.randint(100, 255)
        color = (r, g, b, random.randint(200, 255))
        lifetime = random.randint(4, 10)
        p = Particle(x + random.uniform(-1, 1), y + random.uniform(-1, 1),
                     vx, vy, color, lifetime, size=1,
                     gravity=False, bounce=False)
        world.add(p)

    # Small central flash
    for _ in range(3):
        color = (255, 255, 255, random.randint(100, 200))
        p = Particle(x, y, 0, 0, color, random.randint(2, 5), size=random.randint(1, 2),
                     gravity=False, bounce=False)
        world.add(p)


def spawn_heal(x, y, world, amount=10):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.8, 2.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.8
        g = random.randint(180, 255)
        color = (random.randint(80, 150), g, random.randint(80, 150), random.randint(150, 220))
        lifetime = random.randint(18, 30)
        p = Particle(x + random.uniform(-2, 2), y + random.uniform(-2, 2),
                     vx, vy, color, lifetime, size=1,
                     gravity=True, bounce=True)
        world.add(p)

    # Rising sparkles
    for _ in range(5):
        vx = random.uniform(-0.3, 0.3)
        vy = random.uniform(-1.5, -0.5)
        color = (random.randint(150, 255), random.randint(200, 255), random.randint(150, 255), 200)
        p = Particle(x + random.uniform(-4, 4), y, vx, vy, color, random.randint(15, 25), size=1,
                     gravity=False, bounce=False)
        world.add(p)


def spawn_bones(x, y, world, amount=6):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 1.8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.3
        val = random.randint(180, 230)
        color = (val, val, val - 20, random.randint(180, 255))
        lifetime = random.randint(20, 40)
        p = Particle(x + random.uniform(-1, 1), y + random.uniform(-1, 1),
                     vx, vy, color, lifetime, size=2,
                     gravity=True, bounce=True)
        world.add(p)
