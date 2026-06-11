import math
import random

from PIL import Image, ImageDraw

from Engine import engine as e
from Entities.Item import Item
from Entities.Object import Object


class Bomb(Item):
    def __init__(self, x, y, w, h, bank, parent=None,
                 name="Bomb", damage=60, explosion_radius=40, fuse=60,
                 dropped_pos=(0, 0), image_x=0, image_y=0):
        super().__init__(x, y, w, h, bank, parent,
                         name=name, stackable=True, max_stack=8)
        self.damage = damage
        self.explosion_radius = explosion_radius
        self.fuse = fuse
        self.dropped_pos = dropped_pos
        self.radius = 7
        self.pos_angle = 0

    def update(self):
        super().update()
        if not self.picked_up or not self.parent:
            return
        if hasattr(self.parent, "target"):
            return

        mouse_angle = math.atan2(
            e._global_mouse_pos[1] - self.parent.y,
            e._global_mouse_pos[0] - self.parent.x,
        )

        diff = (mouse_angle - self.pos_angle + math.pi) % (2 * math.pi) - math.pi
        self.pos_angle += diff * 0.2

        self.x = self.parent.x + self.radius * math.cos(self.pos_angle)
        self.y = self.parent.y + self.radius * math.sin(self.pos_angle)

        if e.mouse_btnp(e.MOUSE_BUTTON_LEFT):
            self.throw()

    def throw(self):
        target_x = e._global_mouse_pos[0]
        target_y = e._global_mouse_pos[1]
        bx = self.parent.x + self.parent.w / 2
        by = self.parent.y + self.parent.h / 2
        world = getattr(self, 'world', None) or getattr(self.parent, 'world', None)
        proj = BombProjectile(
            bx, by, target_x, target_y,
            world=world,
            shooter=self.parent,
            damage=self.damage,
            fuse=self.fuse,
            explosion_radius=self.explosion_radius,
            bank=self.bank,
        )
        if world:
            world.add(proj)

        old_qty = self.quantity
        self.quantity -= 1
        if self.quantity <= 0 and old_qty > 0:
            parent = self.parent
            if hasattr(parent, '_remove_item'):
                parent._remove_item(self)
                if hasattr(parent, '_sync_current_item'):
                    parent._sync_current_item()

    def draw(self):
        if not self.picked_up:
            self.draw_image(self.dropped_pos[0], self.dropped_pos[1])
        elif self.parent and self.parent.current_item == self:
            self.draw_image(self.dropped_pos[0], self.dropped_pos[1])


class BombProjectile(Object):
    SPEED = 6.0

    def __init__(self, x, y, target_x, target_y, world, shooter, damage, fuse, explosion_radius, bank):
        super().__init__(x, y, 6, 6, bank)
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.world = world
        self.shooter = shooter
        self.damage = damage
        self.fuse = fuse
        self.explosion_radius = explosion_radius
        self.lifetime = 300
        self.hitbox_inset = 1

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy) or 1
        perp = math.atan2(dy, dx) + math.pi / 2
        self._perp_angle = perp
        self._frames = max(1, int(dist / self.SPEED))
        self._progress = 0.0
        self._arc_amp = random.uniform(0.12, 0.22) * dist * random.choice([-1, 1])
        self._sprite = None
        self._make_sprite()

    def _make_sprite(self):
        w, h = 8, 8
        spr = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(spr)
        draw.ellipse([1, 2, w - 2, h - 1], fill=(55, 50, 45))
        draw.line([w // 2, 2, w // 2 + 1, 0], fill=(180, 140, 60), width=1)
        spr.putpixel((w // 2 + 1, 0), (255, 220, 80))
        self._sprite = spr

    def update(self):
        super().update()

        self._progress += 1.0 / self._frames
        if self._progress >= 1.0:
            self._progress = 1.0
            t = 1.0
        else:
            t = self._progress * self._progress * (3 - 2 * self._progress)

        bx = self.start_x + (self.target_x - self.start_x) * t
        by = self.start_y + (self.target_y - self.start_y) * t
        arc = math.sin(t * math.pi) * self._arc_amp
        self.x = bx + math.cos(self._perp_angle) * arc
        self.y = by + math.sin(self._perp_angle) * arc

        if self._progress >= 1.0:
            self.explode()
            return

        if self.world:
            for entity in self.world.get_nearby(self.x + self.w / 2, self.y + self.h / 2, 12):
                if entity is self or entity is self.shooter or not hasattr(entity, 'take_damage'):
                    continue
                if not getattr(entity, 'is_living', False) and not getattr(entity, 'blocking', False):
                    continue
                dx = entity.x + entity.w / 2 - self.x
                dy = entity.y + entity.h / 2 - self.y
                if dx * dx + dy * dy < 64:
                    self.explode()
                    return

    def explode(self):
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        r = self.explosion_radius
        r2 = r * r

        if self.world:
            for entity in self.world.get_nearby(cx, cy, r + 12):
                if entity is self or entity is self.shooter:
                    continue
                if not hasattr(entity, 'take_damage'):
                    continue
                if not entity.is_living and not getattr(entity, 'blocking', False):
                    continue
                dx = entity.x + entity.w / 2 - cx
                dy = entity.y + entity.h / 2 - cy
                d2 = dx * dx + dy * dy
                if d2 < r2:
                    dist = math.sqrt(d2) if d2 > 0 else 1
                    falloff = 1.0 - (dist / r)
                    dmg = max(1, int(self.damage * falloff))
                    angle = math.atan2(dy, dx) if d2 > 0 else 0
                    entity.take_damage(dmg, self.world, angle=angle)

            try:
                from Entities.Particle import Particle

                for _ in range(30):
                    a = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1.5, 5.0)
                    pvx = math.cos(a) * speed
                    pvy = math.sin(a) * speed
                    rn = random.randint(200, 255)
                    gn = random.randint(100, 200)
                    bn = random.randint(20, 80)
                    color = (rn, gn, bn, random.randint(180, 255))
                    p = Particle(cx + random.uniform(-3, 3), cy + random.uniform(-3, 3),
                                 pvx, pvy, color, random.randint(10, 25), size=1,
                                 gravity=False, bounce=False)
                    self.world.add(p)

                for _ in range(12):
                    a = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0.5, 2.0)
                    pvx = math.cos(a) * speed
                    pvy = math.sin(a) * speed - 0.5
                    val = random.randint(60, 120)
                    color = (val, val, val, random.randint(60, 140))
                    p = Particle(cx + random.uniform(-4, 4), cy + random.uniform(-4, 4),
                                 pvx, pvy, color, random.randint(20, 40), size=2,
                                 gravity=False, bounce=False)
                    self.world.add(p)

                for _ in range(15):
                    a = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2.0, 6.0)
                    pvx = math.cos(a) * speed
                    pvy = math.sin(a) * speed
                    color = (255, random.randint(200, 255), random.randint(100, 255), random.randint(180, 255))
                    p = Particle(cx, cy, pvx, pvy, color, random.randint(5, 12), size=1,
                                 gravity=True, bounce=True)
                    self.world.add(p)

                for _ in range(5):
                    color = (255, 255, 255, random.randint(100, 200))
                    p = Particle(cx, cy, 0, 0, color, random.randint(2, 5), size=random.randint(1, 3),
                                 gravity=False, bounce=False)
                    self.world.add(p)
            except ImportError:
                pass

            if hasattr(e, 'active_camera'):
                e.active_camera.shake(8, 6)
                e.active_camera.flash((255, 200, 100), 30, 8)

        self.lifetime = 0

    def draw(self):
        if self._sprite:
            e.graphics.screen.blit(self._sprite, (
                int(self.x + e.graphics._camera_x),
                int(self.y + e.graphics._camera_y),
            ))
