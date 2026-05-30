import math
import random
from Engine import engine as e

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color  # Expected to be an RGBA tuple (R, G, B, A)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Simple friction
        self.vx *= 0.9
        self.vy *= 0.9

        self.lifetime -= 1

    def draw(self):
        if self.lifetime <= 0:
            return
            
        # Calculate alpha based on lifetime
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Create an RGBA color based on the provided color
        if len(self.color) == 4:
            draw_color = (self.color[0], self.color[1], self.color[2], min(alpha, self.color[3]))
        else:
            draw_color = (self.color[0], self.color[1], self.color[2], alpha)
            
        if self.size <= 1:
            e.pset(int(self.x), int(self.y), draw_color)
        else:
            # We can draw small rects for bigger particles
            # Pygame can handle RGBA filled rects if we use an intermediate surface, 
            # but for simplicity, we'll draw individual pixels if needed, or rely on e.rect.
            # e.rect might ignore alpha if drawn directly to the main screen,
            # but virtual_screen has SRCALPHA now so it should work.
            e.rect(int(self.x), int(self.y), self.size, self.size, draw_color)


def spawn_blood(x, y, world, amount=10):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Red tones
        color = (random.randint(180, 255), 0, 0,255)
        lifetime = random.randint(15, 30)
        
        p = Particle(x, y, vx, vy, color, lifetime, size=1)
        world.add(p)

def spawn_dust(x, y, world, amount=3):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.1, 0.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Gray / Brown tones
        val = random.randint(100, 150)
        color = (val, val - 10, val - 20, 150)
        lifetime = random.randint(10, 20)
        
        p = Particle(x, y, vx, vy, color, lifetime, size=1)
        world.add(p)

def spawn_hit(x, y, world, amount=5):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 3.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Sparkles (White / Yellow)
        color = (255, 255, random.randint(150, 255), 255)
        lifetime = random.randint(5, 10)
        
        p = Particle(x, y, vx, vy, color, lifetime, size=random.randint(1, 2))
        world.add(p)


def spawn_heal(x, y, world, amount=6):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 1.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.5
        color = (100, 255, 100, 200)
        lifetime = random.randint(15, 25)
        p = Particle(x, y, vx, vy, color, lifetime, size=random.randint(1, 2))
        world.add(p)


def spawn_bones(x, y, world, amount=4):
    for _ in range(amount):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3, 1.2)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        val = random.randint(180, 220)
        color = (val, val, val - 20, 255)
        lifetime = random.randint(15, 30)
        p = Particle(x, y, vx, vy, color, lifetime, size=random.randint(1, 2))
        world.add(p)
