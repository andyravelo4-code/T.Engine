import math
from PIL import Image, ImageDraw, ImageFilter
from Engine import engine as e
from Entities.Block import Block


class Light:
    def __init__(self, x, y, radius, color=(255, 255, 200), intensity=1.0, num_rays=32,
                 reflective_bounce=True, angle=0, arc_degrees=360):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.num_rays = num_rays
        self.reflective_bounce = reflective_bounce
        self.angle = angle  # direction the light faces (radians), 0 = right
        self.arc_degrees = arc_degrees  # spread angle (360 = full circle)
        self.ray_ends = []
        self.bounce_ends = []
        self._prev_ray_ends = None
        self._prev_bounce_ends = None

    def update(self, world):
        arc_rad = math.radians(self.arc_degrees)
        start = self.angle - arc_rad / 2
        new_ray_ends = []
        new_bounce_ends = []
        for i in range(self.num_rays):
            t = (i / self.num_rays) if self.num_rays > 1 else 0.5
            angle = start + arc_rad * t
            end, bounce = self._cast_ray(angle, world)
            new_ray_ends.append(end)
            new_bounce_ends.append(bounce)

        if self._prev_ray_ends is not None and len(self._prev_ray_ends) == self.num_rays:
            self.ray_ends = [
                ((ex + self._prev_ray_ends[i][0]) * 0.5,
                 (ey + self._prev_ray_ends[i][1]) * 0.5)
                for i, (ex, ey) in enumerate(new_ray_ends)
            ]
            self.bounce_ends = [
                (bounce if bounce is None else
                 ((bounce[0] + (self._prev_bounce_ends[i][0] if self._prev_bounce_ends[i] else bounce[0])) * 0.5,
                  (bounce[1] + (self._prev_bounce_ends[i][1] if self._prev_bounce_ends[i] else bounce[1])) * 0.5))
                for i, bounce in enumerate(new_bounce_ends)
            ]
        else:
            self.ray_ends = new_ray_ends
            self.bounce_ends = new_bounce_ends

        self._prev_ray_ends = list(self.ray_ends)
        self._prev_bounce_ends = list(self.bounce_ends)

    def _cast_ray(self, angle, world):
        dx = math.cos(angle)
        dy = math.sin(angle)
        max_dist = self.radius
        step = 2
        cx, cy = self.x, self.y

        hit_x, hit_y = None, None
        for dist in range(0, int(max_dist), step):
            px = cx + dx * dist
            py = cy + dy * dist
            blocked = False
            for entity in world.get_nearby(px, py, 4):
                if isinstance(entity, Block) and entity.blocking:
                    if entity.x < px < entity.x + entity.w and entity.y < py < entity.y + entity.h:
                        hit_x, hit_y = px, py
                        blocked = True
                        break
            if blocked:
                break
        else:
            return ((cx + dx * max_dist, cy + dy * max_dist), None)

        bounce = None
        if self.reflective_bounce and self._is_reflective(hit_x, hit_y, world):
            normal = self._get_normal(hit_x, hit_y, dx, dy, world)
            if normal:
                dot = dx * normal[0] + dy * normal[1]
                rdx = dx - 2 * dot * normal[0]
                rdy = dy - 2 * dot * normal[1]
                bounce_dist = min(max_dist * 0.5, max_dist - math.sqrt((hit_x - cx)**2 + (hit_y - cy)**2))
                for bd in range(2, int(bounce_dist), step):
                    bx = hit_x + rdx * bd
                    by = hit_y + rdy * bd
                    bounced = False
                    for entity in world.get_nearby(bx, by, 4):
                        if isinstance(entity, Block) and entity.blocking:
                            if entity.x < bx < entity.x + entity.w and entity.y < by < entity.y + entity.h:
                                bounce = (bx, by)
                                bounced = True
                                break
                    if bounced:
                        break
                else:
                    bounce = (hit_x + rdx * bounce_dist, hit_y + rdy * bounce_dist)

        return ((hit_x, hit_y), bounce)

    def _is_reflective(self, x, y, world):
        for entity in world.get_nearby(x, y, 4):
            if isinstance(entity, Block) and entity.blocking:
                if entity.x < x < entity.x + entity.w and entity.y < y < entity.y + entity.h:
                    return getattr(entity, 'reflective', False)
        return False

    def _get_normal(self, x, y, dx, dy, world):
        for entity in world.get_nearby(x, y, 4):
            if isinstance(entity, Block) and entity.blocking:
                if entity.x < x < entity.x + entity.w and entity.y < y < entity.y + entity.h:
                    b = entity
                    ol = (b.x + b.w) - x
                    orr = x - b.x
                    ot = (b.y + b.h) - y
                    ob = y - b.y
                    m = min(ol, orr, ot, ob)
                    if m == ol:
                        return (-1, 0)
                    elif m == orr:
                        return (1, 0)
                    elif m == ot:
                        return (0, -1)
                    else:
                        return (0, 1)
        return None

    def _polygon_for_rays(self, ends, cam_x, cam_y):
        pts = [(self.x + cam_x, self.y + cam_y)]
        for rx, ry in ends:
            pts.append((rx + cam_x, ry + cam_y))
        return pts


def render_light_overlay(world, cam_x, cam_y):
    sw = e.width()
    sh = e.height()

    darkness = Image.new('RGBA', (sw, sh), (0, 0, 0, 200))
    mask = Image.new('L', (sw, sh), 0)
    draw = ImageDraw.Draw(mask)

    for light in getattr(world, 'lights', []):
        sx = light.x + cam_x
        sy = light.y + cam_y
        if sx < -light.radius or sx > sw + light.radius or sy < -light.radius or sy > sh + light.radius:
            continue

        ends = light.ray_ends
        if not ends:
            continue

        poly = [(sx, sy)]
        for rx, ry in ends:
            poly.append((rx + cam_x, ry + cam_y))
        if light.arc_degrees >= 360 and ends:
            rx0, ry0 = ends[0]
            poly.append((rx0 + cam_x, ry0 + cam_y))
        if len(poly) >= 3:
            draw.polygon(poly, fill=255)

        for bounce in light.bounce_ends:
            if bounce is None:
                continue
            bpoly = [(sx, sy)]
            bpoly.append((bounce[0] + cam_x, bounce[1] + cam_y))
            if len(bpoly) >= 3:
                draw.polygon(bpoly, fill=180)

    if mask.getextrema() != (0, 0):
        mask = mask.filter(ImageFilter.GaussianBlur(radius=3))

    transparent = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    result = Image.composite(transparent, darkness, mask)
    return result
