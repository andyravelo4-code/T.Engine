import heapq
import math

from PIL import Image, ImageDraw

from Engine import engine as e
from Entities.Object import Object


class Npc(Object):
    def __init__(
        self, x, y, w, h, target, frames_dict, world,
        aggressive=True, max_health=100,
        speed=0.5, detection_radius=20, attack_radius=8,
        punch_damage=5, punch_duration=10, punch_cooldown=40,
    ):
        super().__init__(x, y, w, h, frames_dict["bank"])
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

    def get_grid_pos(self, x, y):
        # We assume 8x8 grid cells for pathfinding
        return int(round(x) // 8), int(round(y) // 8)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start_pos, goal_pos, world):
        start = self.get_grid_pos(*start_pos)
        goal = self.get_grid_pos(*goal_pos)

        # Borne la zone de recherche pour éviter l'explosion infinie
        pad = 30
        min_x = min(start[0], goal[0]) - pad
        max_x = max(start[0], goal[0]) + pad
        min_y = min(start[1], goal[1]) - pad
        max_y = max(start[1], goal[1]) + pad

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        # Build set of blocking grid positions
        obstacles = set()
        for obj in world.entities:
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

    def draw(self):
        # Draw shadow
        shadow_x, shadow_y = self.frames_dict.get("shadow", (4, 0))
        e.blt(int(self.x), int(self.y + 1), self.bank, (self.image_x + shadow_x) * 8, (self.image_y + shadow_y) * 8, 8, 8)
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

        # Draw punch arc
        if self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            alpha = int(255 * (1.0 - progress))
            surf = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(surf)
            center = (16, 16)
            radius = 8 + progress * 3
            points = []
            for i in range(-80, 81, 8):
                rad = math.radians(i) + self.punch_angle
                px = center[0] + math.cos(rad) * radius
                py = center[1] + math.sin(rad) * radius
                points.append((px, py))
            for i in range(80, -81, -8):
                rad = math.radians(i) + self.punch_angle
                thickness = 2.5 * math.cos(math.radians(i / 80 * 90))
                r = radius - thickness
                px = center[0] + math.cos(rad) * r
                py = center[1] + math.sin(rad) * r
                points.append((px, py))
            if len(points) >= 3:
                draw.polygon(points, fill=(255, 255, 255, alpha))
            e.graphics.screen.blit(surf, (self.x + self.w/2 - 16 + e.graphics._camera_x, self.y + self.h/2 - 16 + e.graphics._camera_y))

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

        # Interaction with items
        if not self.current_item:
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
            self.current_item.update()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.direction = "idle"
        dist = math.hypot(self.target.x - self.x, self.target.y - self.y)

        # Dynamic attack radius
        current_attack_radius = self.attack_radius
        from Items.Crossbow import Crossbow

        if isinstance(self.current_item, Crossbow):
            current_attack_radius = 60

        if self.aggressive and dist < current_attack_radius:
            self.state = "attack" if world.active_npc is self else "idle"
            if self.state == "attack":
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
            if self.state == "idle":
                self.path = []

        if self.is_punching:
            self.punch_timer -= 1
            for entity in world.entities:
                if entity is self or not hasattr(entity, 'take_damage'):
                    continue
                if not entity.is_living and not getattr(entity, 'blocking', False):
                    continue
                p_dist = math.hypot(entity.x + entity.w/2 - self.x, entity.y + entity.h/2 - self.y)
                if p_dist < 18 and entity not in self.hit_entities:
                    angle_to_entity = math.atan2(entity.y + entity.h/2 - (self.y + self.h/2), entity.x + entity.w/2 - (self.x + self.w/2))
                    angle_diff = (angle_to_entity - self.punch_angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) < math.radians(90):
                        self.hit_entities.append(entity)
                        entity.take_damage(self.punch_damage, self.world)
            if self.punch_timer <= 0:
                self.is_punching = False
        elif self.aggressive and dist < self.detection_radius:
            self.state = "chase" if world.active_npc is self else "idle"
            if self.state == "chase":
                self.path_timer -= 1
                if self.path_timer <= 0:
                    start_pos = (self.path[0][0]*8, self.path[0][1]*8) if self.path else (self.x, self.y)
                    new_path = self.a_star(start_pos, (self.target.x, self.target.y), world)
                    if self.path and new_path:
                        if new_path[0] == self.path[0]:
                            new_path.pop(0)
                        self.path = [self.path[0]] + new_path
                    else:
                        self.path = new_path
                    self.path_timer = self.path_delay

                if self.path:
                    next_node = self.path[0]
                    target_x = next_node[0] * 8
                    target_y = next_node[1] * 8

                    dx = target_x - self.x
                    dy = target_y - self.y
                    dist_to_node = math.hypot(dx, dy)

                    if dist_to_node <= self.speed or dist_to_node < 0.01:
                        self.x = target_x
                        self.y = target_y
                        self.path.pop(0)
                    else:
                        move_x = (dx / dist_to_node) * self.speed
                        move_y = (dy / dist_to_node) * self.speed
                        self.x += move_x
                        self.y += move_y

                        if abs(move_x) > abs(move_y):
                            if move_x > 0:
                                self.direction = "right"
                            else:
                                self.direction = "left"
                        else:
                            if move_y > 0:
                                self.direction = "down"
                            else:
                                self.direction = "up"
                                
                        if e.frame_count() % 5 == 0:
                            try:
                                from Entities.Particle import spawn_dust
                                spawn_dust(self.x + self.w / 2, self.y + self.h, world, amount=1)
                            except ImportError:
                                pass
            if self.state == "idle":
                self.path = []
        else:
            self.state = "idle"
            self.path = []

        super().update()

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
