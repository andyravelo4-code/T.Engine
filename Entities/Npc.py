import heapq
import math

from Engine import engine as e
from Entities.Object import Object


class Npc(Object):
    def __init__(
        self, x, y, w, h, bank, target, frames_dict, world, image_x=0, image_y=0, aggressive=True, max_health=100
    ):
        super().__init__(x, y, w, h, bank)
        self.aggressive = aggressive
        self.max_health = max_health
        self.health = max_health
        self.target = target
        self.frames_dict = frames_dict
        self.world = world
        self.image_x = image_x
        self.image_y = image_y
        self.last_dir = "left"
        self.speed = 0.5
        self.state = "idle"
        self.detection_radius = 40
        self.attack_radius = 12
        self.attack_cooldown = 0
        self.path = []
        self.path_timer = 0
        self.path_delay = 30  # Recalculate path every 30 frames

    def get_grid_pos(self, x, y):
        # We assume 8x8 grid cells for pathfinding
        return int(round(x) // 8), int(round(y) // 8)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start_pos, goal_pos, world):
        start = self.get_grid_pos(*start_pos)
        goal = self.get_grid_pos(*goal_pos)

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

            # 4-way movement
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_node = (current[0] + dx, current[1] + dy)
                if next_node in obstacles:
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
            return []  # No path found

        while current != start:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def draw(self):
        # Draw shadow like player
        e.blt(int(self.x), int(self.y + 1), self.bank, 4 * 8, 0 * 8, 8, 8)
        match self.direction:
            case "idle":
                dir_key = f"idle_{self.last_dir}"
                self.animate(0, self.frames_dict.get(dir_key, 4), 5, 4)
            case "up":
                self.animate(0, self.frames_dict.get("walk_up", 2), 6, 4)
                self.last_dir = "up"
            case "down":
                self.animate(0, self.frames_dict.get("walk_down", 3), 6, 4)
                self.last_dir = "down"
            case "left":
                self.animate(0, self.frames_dict.get("walk_left", 1), 6, 4)
                self.last_dir = "left"
            case "right":
                self.animate(0, self.frames_dict.get("walk_right", 0), 6, 4)
                self.last_dir = "right"
        super().draw()
        if self.current_item:
            self.current_item.draw()
            
        # Draw health dot
        health_ratio = max(0, self.health / self.max_health)
        if health_ratio > 0.6:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
            
        e.circ(int(self.x + self.w / 2), int(self.y), 1, color)

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
        from Entities.Crossbow import Crossbow

        if isinstance(self.current_item, Crossbow):
            current_attack_radius = 60

        if self.aggressive and dist < current_attack_radius:
            self.state = "attack"
            self._face_target()
            if self.current_item and self.attack_cooldown <= 0:
                if hasattr(self.current_item, "slash") and not getattr(
                    self.current_item, "is_slashing", False
                ):
                    self.current_item.slash()
                    self.attack_cooldown = 60
                elif hasattr(self.current_item, "fire") and not getattr(
                    self.current_item, "is_firing", False
                ):
                    angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
                    self.current_item.fire(angle)
                    self.attack_cooldown = 60
        elif self.aggressive and dist < self.detection_radius:
            self.state = "chase"
            self.path_timer -= 1
            if self.path_timer <= 0:
                self.path = self.a_star(
                    (self.x, self.y), (self.target.x, self.target.y), world
                )
                self.path_timer = self.path_delay

            if self.path:
                next_node = self.path[0]
                target_x = next_node[0] * 8
                target_y = next_node[1] * 8

                dx = target_x - self.x
                dy = target_y - self.y
                dist_to_node = math.hypot(dx, dy)

                if dist_to_node <= self.speed:
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
