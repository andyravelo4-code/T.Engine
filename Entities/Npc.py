import heapq
import math
import random

from PIL import Image, ImageDraw

from Engine import engine as e
from Entities.Object import Object


class Npc(Object):
    def __init__(
        self, x, y, w, h, target, frames_dict, world,
        aggressive=True, max_health=100,
        speed=0.3, detection_radius=20, attack_radius=10,
        punch_damage=5, punch_duration=10, punch_cooldown=40,
        name="",
    ):
        super().__init__(x, y, w, h, frames_dict["bank"])
        self.name = name
        self.aggressive = aggressive
        self.max_health = max_health
        self.health = max_health
        self.target = target
        self.frames_dict = frames_dict
        self.world = world
        self.image_x = frames_dict["image_x"]
        self.image_y = frames_dict["image_y"]
        self.is_living = True
        self.last_dir = "left"
        self.speed = speed
        self.state = "idle"
        self.detection_radius = detection_radius
        self.attack_radius = attack_radius
        self.attack_cooldown = 0
        self.path = []
        self.path_timer = 0
        self.path_delay = 15
        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = punch_duration
        self.punch_angle = 0
        self.punch_damage = punch_damage
        self.punch_cooldown = punch_cooldown
        self.hit_entities = []

        # Non-aggressive behavior
        self._behavior_timer = 0
        self._idle_timer = 0
        self._wander_target = None
        self._hit_flee_timer = 0
        self._aggro = False
        self._target_x = None
        self._target_y = None
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self._rem_x = 0.0
        self._rem_y = 0.0
        self.acceleration = 0.15
        self.friction = 0.85
        self.max_speed = 1.2

    def get_grid_pos(self, x, y):
        # We assume 8x8 grid cells for pathfinding
        return int(round(x) // 8), int(round(y) // 8)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start_pos, goal_pos, world):
        start = self.get_grid_pos(*start_pos)
        goal = self.get_grid_pos(*goal_pos)
        map_entity = getattr(world, "map", None)

        # Borne la zone de recherche pour éviter l'explosion infinie
        pad = 30
        min_x = max(0, min(start[0], goal[0]) - pad)
        max_x = min(map_entity.width - 1, max(start[0], goal[0]) + pad) if map_entity else max(start[0], goal[0]) + pad
        min_y = max(0, min(start[1], goal[1]) - pad)
        max_y = min(map_entity.height - 1, max(start[1], goal[1]) + pad) if map_entity else max(start[1], goal[1]) + pad

        # Clamp goal to map bounds
        if map_entity:
            goal = (max(0, min(goal[0], map_entity.width - 1)),
                    max(0, min(goal[1], map_entity.height - 1)))

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        # Build set of blocking grid positions (via spatial hash)
        obstacles = set()
        near = world.get_nearby(
            (start_pos[0] + goal_pos[0]) / 2,
            (start_pos[1] + goal_pos[1]) / 2,
            int(math.hypot(start_pos[0] - goal_pos[0], start_pos[1] - goal_pos[1]) / 2 + 32)
        )
        for obj in near:
            if getattr(obj, "blocking", False) and obj != self and obj != self.target:
                obstacles.add(self.get_grid_pos(obj.x, obj.y))

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_node = (current[0] + dx, current[1] + dy)

                if next_node in obstacles:
                    continue

                if not (min_x <= next_node[0] <= max_x and min_y <= next_node[1] <= max_y):
                    continue

                # Skip unwalkable map tiles
                if map_entity:
                    if not (0 <= next_node[1] < map_entity.height and 0 <= next_node[0] < map_entity.width):
                        continue
                    tile = map_entity.grid[next_node[1]][next_node[0]]
                    if not map_entity._is_walkable(tile, next_node[0], next_node[1]):
                        continue

                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(goal, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        path = []
        current = goal
        if current not in came_from:
            return []

        while current != start:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def take_damage(self, amount, world, angle=None):
        if self.aggressive:
            self._aggro = True
        else:
            self._hit_flee_timer = 30
            self.path = []
            self._behavior_timer = 0
        super().take_damage(amount, world, angle=angle)

    def draw(self):
        # Draw shadow
        #shadow_x, shadow_y = self.frames_dict.get("shadow", (4, 0))
        e.elli(self.x,self.y+6,8,4,(0,0,0,70))
        #e.blt(int(self.x), int(self.y + 1), self.bank, (self.image_x + shadow_x) * 8, (self.image_y + shadow_y) * 8, 8, 8)
        match self.direction:
            case "idle":
                dir_key = f"idle_{self.last_dir}"
                anim_x, anim_y = self.frames_dict.get(dir_key, (0, 4))
                self.animate(anim_x, anim_y, 5, 4)
            case "up":
                anim_x, anim_y = self.frames_dict.get("walk_up", (0, 2))
                self.animate(anim_x, anim_y, 6, 4)
                self.last_dir = "up"
            case "down":
                anim_x, anim_y = self.frames_dict.get("walk_down", (0, 3))
                self.animate(anim_x, anim_y, 6, 4)
                self.last_dir = "down"
            case "left":
                anim_x, anim_y = self.frames_dict.get("walk_left", (0, 1))
                self.animate(anim_x, anim_y, 6, 4)
                self.last_dir = "left"
            case "right":
                anim_x, anim_y = self.frames_dict.get("walk_right", (0, 0))
                self.animate(anim_x, anim_y, 6, 4)
                self.last_dir = "right"
        super().draw()
        if self.current_item:
            self.current_item.draw()

        # Draw punch arc (cached PIL frames)
        if self.is_punching:
            if not hasattr(self, '_punch_cache') or getattr(self, '_punch_angle', None) != self.punch_angle:
                self._punch_cache = {}
                self._punch_angle = self.punch_angle
                for t in range(self.punch_duration + 1):
                    progress = 1.0 - t / self.punch_duration
                    alpha = int(255 * (1.0 - progress))
                    radius = 8 + progress * 3
                    surf = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(surf)
                    cx, cy = 16, 16
                    pts = []
                    for i in range(-80, 81, 8):
                        rad = math.radians(i) + self.punch_angle
                        pts.append((cx + math.cos(rad) * radius, cy + math.sin(rad) * radius))
                    for i in range(80, -81, -8):
                        rad = math.radians(i) + self.punch_angle
                        t2 = 2.5 * math.cos(math.radians(i / 80 * 90))
                        r = radius - t2
                        pts.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
                    if len(pts) >= 3:
                        draw.polygon(pts, fill=(255, 255, 255, alpha))
                    self._punch_cache[t] = surf
            e.graphics.screen.blit(self._punch_cache[self.punch_timer], (
                self.x + self.w / 2 - 16 + e.graphics._camera_x,
                self.y + self.h / 2 - 16 + e.graphics._camera_y,
            ))

        # Draw health dot
        health_ratio = max(0, self.health / self.max_health)
        if health_ratio > 0.6:
            color = (95, 255, 129, 60)
        elif health_ratio > 0.3:
            color = (255, 255, 0,70)
        else:
            color = (255, 0, 0,70)

        e.pset(int(self.x-1 + self.w / 2), int(self.y), color)

    def update(self):
        world = self.world
        if not world:
            return

        # Interaction with items — only aggressive NPCs pick up items
        if self.aggressive and not self.current_item:
            from Entities.Item import Item

            for obj in list(world.entities):
                if isinstance(obj, Item) and not obj.picked_up:
                    if self.is_collid(obj):
                        obj.picked_up = True
                        obj.parent = self
                        if hasattr(obj, "world"):
                            obj.world = world
                        self.items.append(obj)
                        self.current_item = obj
                        world.remove(obj)
                        break
        else:
            if self.aggressive and self.current_item:
                self.current_item.update()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.direction = "idle"
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist2 = dx * dx + dy * dy

        # Dynamic attack radius
        current_attack_radius = self.attack_radius
        from Items.Crossbow import Crossbow

        if isinstance(self.current_item, Crossbow):
            current_attack_radius = 60

        # Apply knockback (regardless of state)
        if abs(self.knockback_x) > 0.01 or abs(self.knockback_y) > 0.01:
            world = self.world
            # Apply X
            self.x += self.knockback_x
            if self._collides_at(self.x, self.y, world):
                self.x -= self.knockback_x
                self.knockback_x = 0
            # Apply Y
            self.y += self.knockback_y
            if self._collides_at(self.x, self.y, world):
                self.y -= self.knockback_y
                self.knockback_y = 0

            self.knockback_x *= 0.65
            self.knockback_y *= 0.65
            if abs(self.knockback_x) < 0.05:
                self.knockback_x = 0
            if abs(self.knockback_y) < 0.05:
                self.knockback_y = 0

        if self.stun_timer > 0:
            self.stun_timer -= 1
        else:
            if self.aggressive:
                self._update_aggressive(dist2, current_attack_radius)
            else:
                self._update_passive()

        super().update()

    def _update_aggressive(self, dist2, current_attack_radius):
        world = self.world
        ar2 = current_attack_radius * current_attack_radius

        if self._aggro:
            if dist2 < ar2:
                self.state = "attack"
                self._face_target()
                if self.attack_cooldown <= 0:
                    if self.current_item:
                        if hasattr(self.current_item, "slash") and not getattr(
                            self.current_item, "is_slashing", False
                        ):
                            self.current_item.slash()
                            self.attack_cooldown = getattr(self.current_item, "cooldown", 20)
                        elif hasattr(self.current_item, "fire") and not getattr(
                            self.current_item, "is_firing", False
                        ):
                            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                            self.current_item.fire(angle)
                            self.attack_cooldown = getattr(self.current_item, "cooldown", 30)
                    elif not self.is_punching:
                        self.is_punching = True
                        self.punch_timer = self.punch_duration
                        self.hit_entities = []
                        self.punch_angle = math.atan2(
                            self.target.y - (self.y + self.h/2),
                            self.target.x - (self.x + self.w/2)
                        )
                        self.attack_cooldown = self.punch_cooldown
            else:
                self.state = "chase"
                self._follow_path(self.target.x, self.target.y)
            if self.is_punching:
                self._update_punch()
            return

        if dist2 < ar2:
            self.state = "attack"
            self._face_target()
            if self.attack_cooldown <= 0:
                if self.current_item:
                    if hasattr(self.current_item, "slash") and not getattr(
                        self.current_item, "is_slashing", False
                    ):
                        self.current_item.slash()
                        self.attack_cooldown = getattr(self.current_item, "cooldown", 20)
                    elif hasattr(self.current_item, "fire") and not getattr(
                        self.current_item, "is_firing", False
                    ):
                        angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                        self.current_item.fire(angle)
                        self.attack_cooldown = getattr(self.current_item, "cooldown", 30)
                elif not self.is_punching:
                    self.is_punching = True
                    self.punch_timer = self.punch_duration
                    self.hit_entities = []
                    self.punch_angle = math.atan2(
                        self.target.y - (self.y + self.h/2),
                        self.target.x - (self.x + self.w/2)
                    )
                    self.attack_cooldown = self.punch_cooldown

        if self.is_punching:
            self._update_punch()
        elif dist2 < self.detection_radius * self.detection_radius:
            self.state = "chase"
            self._follow_path(self.target.x, self.target.y)
        else:
            self.state = "idle"
            self.path = []

    def _update_passive(self):
        world = self.world

        # Hit reaction — flee briefly
        if self._hit_flee_timer > 0:
            self._hit_flee_timer -= 1
            self.state = "flee"
            self._target_x = self.x + random.randint(-60, 60)
            self._target_y = self.y + random.randint(-60, 60)
            self._move_smoothly(self._target_x, self._target_y)
            return

        # Flee from aggressive NPCs (priority)
        nearest_threat = None
        nearest_threat_dist2 = float("inf")
        dr2 = self.detection_radius * self.detection_radius
        for entity in world.get_nearby(self.x + self.w / 2, self.y + self.h / 2, self.detection_radius):
            if entity is self:
                continue
            if getattr(entity, "aggressive", False) and entity is not self.target:
                dx = entity.x - self.x
                dy = entity.y - self.y
                d2 = dx * dx + dy * dy
                if d2 < nearest_threat_dist2:
                    nearest_threat_dist2 = d2
                    nearest_threat = entity

        if nearest_threat and nearest_threat_dist2 < dr2:
            self.state = "flee"
            self._target_x = self.x - (nearest_threat.x - self.x) * 3
            self._target_y = self.y - (nearest_threat.y - self.y) * 3
            self._move_smoothly(self._target_x, self._target_y)
            return

        # Pick a new behavior
        self._behavior_timer -= 1
        if self._behavior_timer <= 0:
            roll = random.random()
            if roll < 0.30:
                self.state = "flee"
                self._behavior_timer = random.randint(20, 50)
                self._target_x = self.x + random.randint(-120, 120)
                self._target_y = self.y + random.randint(-120, 120)
            elif roll < 0.50:
                self.state = "idle"
                self._idle_timer = random.randint(15, 45)
                self._behavior_timer = self._idle_timer
                dirs = ["up", "down", "left", "right"]
                self.last_dir = random.choice(dirs)
                self.velocity_x = 0
                self.velocity_y = 0
            else:
                self.state = "walk"
                self._behavior_timer = random.randint(30, 90)
                self._target_x = self.x + random.randint(-80, 80)
                self._target_y = self.y + random.randint(-80, 80)

        # Execute current behavior every frame
        if self.state == "idle":
            self._idle_timer -= 1
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
            if abs(self.velocity_x) < 0.02:
                self.velocity_x = 0
            if abs(self.velocity_y) < 0.02:
                self.velocity_y = 0
            self._apply_velocity()
            if self._idle_timer <= 0:
                self._behavior_timer = 0
        elif self.state in ("flee", "walk"):
            self._move_smoothly(self._target_x, self._target_y)
            dx = self._target_x - self.x
            dy = self._target_y - self.y
            if dx * dx + dy * dy < 64:
                self._behavior_timer = 0

    def _follow_path(self, target_x, target_y):
        world = self.world
        dx = target_x - self.x
        dy = target_y - self.y
        if dx * dx + dy * dy < 64:
            self.path = []
            return

        self.path_timer -= 1
        if self.path_timer <= 0 or not self.path:
            start_pos = (self.path[0][0]*8, self.path[0][1]*8) if self.path else (self.x, self.y)
            new_path = self.a_star(start_pos, (target_x, target_y), world)
            if self.path and new_path:
                if new_path[0] == self.path[0]:
                    new_path.pop(0)
                self.path = [self.path[0]] + new_path
            else:
                self.path = new_path
            self.path_timer = self.path_delay

        if self.path:
            next_node = self.path[0]
            nx = next_node[0] * 8
            ny = next_node[1] * 8
            dx = nx - self.x
            dy = ny - self.y
            nd2 = dx * dx + dy * dy
            map_w, map_h = self._map_bounds(world)
            if nd2 <= self.speed * self.speed or nd2 < 0.0001:
                self.x = max(0, min(nx, map_w - self.w))
                self.y = max(0, min(ny, map_h - self.h))
                self.path.pop(0)
            else:
                nd = math.sqrt(nd2)
                self.x = max(0, min(self.x + (dx / nd) * self.speed, map_w - self.w))
                self.y = max(0, min(self.y + (dy / nd) * self.speed, map_h - self.h))
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down" if dy > 0 else "up"
                if e.frame_count() % 5 == 0:
                    try:
                        from Entities.Particle import spawn_dust
                        spawn_dust(self.x + self.w / 2, self.y + self.h, world, amount=1)
                    except ImportError:
                        pass

    def _move_smoothly(self, target_x, target_y):
        """Steer smoothly toward a target point with obstacle/entity avoidance."""
        world = self.world

        # Clamp target to map bounds
        map_entity = getattr(world, "map", None)
        if map_entity:
            margin = 4
            target_x = max(margin, min(target_x, map_entity.width * 8 - self.w - margin))
            target_y = max(margin, min(target_y, map_entity.height * 8 - self.h - margin))

        dx = target_x - self.x
        dy = target_y - self.y
        dist2 = dx * dx + dy * dy

        if dist2 < 16:
            self.velocity_x *= 0.5
            self.velocity_y *= 0.5
            if dist2 < 1:
                self.velocity_x = 0
                self.velocity_y = 0
                self.state = "idle"
                return

        # Accelerate toward target (4-directional)
        if dist2 > 0:
            if abs(dx) > abs(dy):
                self.velocity_x += (1 if dx > 0 else -1) * self.acceleration
                self.velocity_y *= 0.9
            else:
                self.velocity_y += (1 if dy > 0 else -1) * self.acceleration
                self.velocity_x *= 0.9

        # Entity avoidance — repulsion from nearby blocking entities
        for entity in world.get_nearby(self.x + self.w / 2, self.y + self.h / 2, 16):
            if entity is self or entity is self.target:
                continue
            if not getattr(entity, "blocking", False) and not isinstance(entity, Npc):
                continue
            ex = entity.x + entity.w / 2
            ey = entity.y + entity.h / 2
            sx = self.x + self.w / 2
            sy = self.y + self.h / 2
            edx = sx - ex
            edy = sy - ey
            ed2 = edx * edx + edy * edy
            if 0 < ed2 < 144:
                edist = math.sqrt(ed2)
                force = (12 - edist) / 12 * 0.3
                self.velocity_x += (edx / edist) * force
                self.velocity_y += (edy / edist) * force

        # Friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # Clamp speed
        speed2 = self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y
        max_s2 = self.max_speed * self.max_speed
        if speed2 > max_s2:
            ratio = self.max_speed / math.sqrt(speed2)
            self.velocity_x *= ratio
            self.velocity_y *= ratio

        if abs(self.velocity_x) < 0.02:
            self.velocity_x = 0.0
        if abs(self.velocity_y) < 0.02:
            self.velocity_y = 0.0

        # Set direction from velocity — 4-directional, zero out other axis
        if speed2 > 0.01:
            if abs(self.velocity_x) > abs(self.velocity_y):
                self.direction = "right" if self.velocity_x > 0 else "left"
                self.velocity_y = 0
            else:
                self.direction = "down" if self.velocity_y > 0 else "up"
                self.velocity_x = 0

        # Apply movement
        self._apply_velocity()

        if speed2 > 0.25 and e.frame_count() % 7 == 0:
            try:
                from Entities.Particle import spawn_dust
                spawn_dust(self.x + self.w / 2, self.y + self.h, world, amount=1)
            except ImportError:
                pass

    def _map_bounds(self, world):
        map_entity = getattr(world, "map", None)
        if map_entity:
            return map_entity.width * 8, map_entity.height * 8
        return 999999, 999999

    def _apply_velocity(self):
        """Apply velocity with remainder accumulation, collision, and map bounds clamping."""
        world = self.world
        map_w, map_h = self._map_bounds(world)

        self._rem_x += self.velocity_x
        self._rem_y += self.velocity_y
        dx_step = int(self._rem_x)
        dy_step = int(self._rem_y)
        self._rem_x -= dx_step
        self._rem_y -= dy_step

        if dx_step != 0:
            nx = self.x + dx_step
            nx = max(0, min(nx, map_w - self.w))
            if not self._collides_at(nx, self.y, world):
                self.x = nx
            else:
                self.velocity_x = 0

        if dy_step != 0:
            ny = self.y + dy_step
            ny = max(0, min(ny, map_h - self.h))
            if not self._collides_at(self.x, ny, world):
                self.y = ny
            else:
                self.velocity_y = 0

    def _collides_at(self, x, y, world):
        """Check if position collides with blocking tiles or entities."""
        # Check map tiles
        map_entity = getattr(world, "map", None)
        if map_entity:
            gx = int((x + self.w / 2) // 8)
            gy = int((y + self.h / 2) // 8)
            if 0 <= gy < map_entity.height and 0 <= gx < map_entity.width:
                if not map_entity._is_walkable(map_entity.grid[gy][gx], gx, gy):
                    return True
        # Check blocking entities (via spatial hash)
        for entity in world.get_nearby(x + self.w / 2, y + self.h / 2, 12):
            if entity is self:
                continue
            if getattr(entity, "blocking", False):
                if (x < entity.x + entity.w and x + self.w > entity.x and
                    y < entity.y + entity.h and y + self.h > entity.y):
                    return True
        return False

    def _update_punch(self):
        self.punch_timer -= 1
        for entity in self.world.get_nearby(self.x + self.w / 2, self.y + self.h / 2, 24):
            if entity is self or not hasattr(entity, 'take_damage'):
                continue
            if not entity.is_living and not getattr(entity, 'blocking', False):
                continue
            dx = entity.x + entity.w/2 - self.x
            dy = entity.y + entity.h/2 - self.y
            if dx * dx + dy * dy < 324 and entity not in self.hit_entities:
                angle_to_entity = math.atan2(entity.y + entity.h/2 - (self.y + self.h/2), entity.x + entity.w/2 - (self.x + self.w/2))
                angle_diff = (angle_to_entity - self.punch_angle + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) < math.radians(90):
                    self.hit_entities.append(entity)
                    entity.take_damage(self.punch_damage, self.world, angle=self.punch_angle)
        if self.punch_timer <= 0:
            self.is_punching = False

    def _face_target(self):
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        if abs(dx) > abs(dy):
            if dx > 0:
                self.last_dir = "right"
            else:
                self.last_dir = "left"
        else:
            if dy > 0:
                self.last_dir = "down"
            else:
                self.last_dir = "up"
