import math
from PIL import Image, ImageDraw

from Engine import engine as e
from Entities.Object import Object
from Entities.Npc import Npc


class Player(Object):
    MAX_STORAGE = 25
    MAX_CRAFTING = 4
    MAX_EQUIP = 2

    def __init__(self, x, y, w, h, bank, world=None, image_x=0, image_y=0):
        super().__init__(x, y, w, h, bank)
        self.world = world
        self.image_x = image_x
        self.image_y = image_y
        self.is_living = True
        self.hitbox_inset = 1
        self.last_dir = "left"
        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 10
        self.punch_angle = 0
        self.hit_entities = []
        self.items = [None] * self.MAX_STORAGE
        self.crafting = [None] * self.MAX_CRAFTING
        self.equipment = [None, None]
        self.current_item = None
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self._rem_x = 0.0
        self._rem_y = 0.0
        self.acceleration = 0.35
        self.friction = 0.85
        self.max_speed = 1.4

    def draw(self):
        e.blt(
            self.x,
            self.y + 1,
            self.bank,
            (self.image_x + 4) * 8,
            (self.image_y + 0) * 8,
            8,
            8,
        )

        last_dir_dict = {"up": 6, "down": 7, "left": 5, "right": 4}
        match self.direction:
            case "idle":
                self.animate(0, last_dir_dict[self.last_dir], 5, 4)
            case "up":
                self.animate(0, 2, 5, 4)
                self.last_dir = "up"
            case "down":
                self.animate(0, 3, 5, 4)
                self.last_dir = "down"
            case "left":
                self.animate(0, 1, 5, 4)
                self.last_dir = "left"
            case "right":
                self.last_dir = "right"
                self.animate(0, 0, 5, 4)
        super().draw()
        if self.current_item:
            self.current_item.draw()

        health_ratio = max(0, self.health / self.max_health)
        if health_ratio > 0.6:
            color = (95, 255, 129, 60)
        elif health_ratio > 0.3:
            color = (255, 255, 0, 60)
        else:
            color = (255, 0, 0, 60)

        e.pset(int(self.x-1 + self.w / 2), int(self.y-1), color)

        if self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            alpha = int(255 * (1.0 - progress))
            surf = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(surf)

            center = (16, 16)
            radius = 7 + progress * 3
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

            e.graphics.screen.blit(surf, (
                self.x + self.w / 2 - 16 + e.graphics._camera_x,
                self.y + self.h / 2 - 16 + e.graphics._camera_y,
            ))

    def update(self):
        world = self.world
        self.direction = "idle"

        if self.current_item:
            self.current_item.update()

        if e.btnp(e.KEY_E):
            from Entities.Item import Item

            for obj in list(world.entities):
                if isinstance(obj, Item) and not obj.picked_up:
                    if self.is_collid(obj):
                        added = self._add_to_storage(obj)
                        if added:
                            obj.picked_up = True
                            obj.parent = self
                            if hasattr(obj, "world"):
                                obj.world = world
                            world.remove(obj)
                            self._sync_current_item()
                        break

        if e.btnp(e.KEY_R) and self.current_item:
            item_to_drop = self.current_item
            self._remove_item(item_to_drop)
            item_to_drop.picked_up = False
            item_to_drop.parent = None
            item_to_drop.x = self.x
            item_to_drop.y = self.y
            world.add(item_to_drop)
            self._sync_current_item()

        if e.btnp(e.KEY_F):
            self._cycle_weapon()

        moving = False

        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        if e.btn(e.KEY_W) or e.btn(e.KEY_Z):
            self.direction = "up"
            self.velocity_y -= self.acceleration
            self.last_dir = "up"
            moving = True
        if e.btn(e.KEY_S):
            self.direction = "down"
            self.velocity_y += self.acceleration
            self.last_dir = "down"
            moving = True
        if e.btn(e.KEY_A) or e.btn(e.KEY_Q):
            self.direction = "left"
            self.velocity_x -= self.acceleration
            self.last_dir = "left"
            moving = True
        if e.btn(e.KEY_D):
            self.direction = "right"
            self.velocity_x += self.acceleration
            self.last_dir = "right"
            moving = True

        if abs(self.velocity_x) < 0.05:
            self.velocity_x = 0.0
        if abs(self.velocity_y) < 0.05:
            self.velocity_y = 0.0

        speed = math.hypot(self.velocity_x, self.velocity_y)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.velocity_x *= ratio
            self.velocity_y *= ratio

        if not moving and speed > 0.30:
            moving = True
            if abs(self.velocity_x) > abs(self.velocity_y):
                self.direction = "right" if self.velocity_x > 0 else "left"
            else:
                self.direction = "down" if self.velocity_y > 0 else "up"
            self.last_dir = self.direction

        self._rem_x += self.velocity_x
        self._rem_y += self.velocity_y

        if not self.current_item and self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            lunge_speed = 3.5 * (1.0 - progress)
            self._rem_x += math.cos(self.punch_angle) * lunge_speed
            self._rem_y += math.sin(self.punch_angle) * lunge_speed
            moving = True

        if self.current_item and getattr(self.current_item, "is_slashing", False):
            if hasattr(self, "target"):
                target_x = self.target.x
                target_y = self.target.y
            else:
                target_x = e._global_mouse_pos[0]
                target_y = e._global_mouse_pos[1]

            slash_angle = math.atan2(target_y - self.y, target_x - self.x)
            progress = 1.0 - (self.current_item.slash_timer / self.current_item.slash_duration)
            lunge_speed = 4.5 * (1.0 - progress)
            self._rem_x += math.cos(slash_angle) * lunge_speed
            self._rem_y += math.sin(slash_angle) * lunge_speed
            moving = True            

        dx = int(self._rem_x)
        dy = int(self._rem_y)
        self._rem_x -= dx
        self._rem_y -= dy

        if dx != 0:
            self.x += dx
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self and not isinstance(obj, Npc):
                    if self.is_collid(obj):
                        self.x -= dx
                        break

        if dy != 0:
            self.y += dy
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self and not isinstance(obj, Npc):
                    if self.is_collid(obj):
                        self.y -= dy
                        break

        if self.is_punching or (self.current_item and getattr(self.current_item, "is_slashing", False)):
            angle = math.atan2(
                e._global_mouse_pos[1] - (self.y + self.h / 2),
                e._global_mouse_pos[0] - (self.x + self.w / 2),
            )
            deg = math.degrees(angle)
            if -45 <= deg <= 45:
                self.last_dir = "right"
            elif 45 < deg <= 135:
                self.last_dir = "down"
            elif deg > 135 or deg <= -135:
                self.last_dir = "left"
            elif -135 < deg < -45:
                self.last_dir = "up"
            self.direction = "idle"

        if not moving:
            mouse_angle = math.atan2(
                e._global_mouse_pos[1] - self.y, e._global_mouse_pos[0] - self.x
            )
            deg = math.degrees(mouse_angle)

            if -45 <= deg <= 45:
                self.last_dir = "right"
            elif 45 < deg <= 135:
                self.last_dir = "down"
            elif deg > 135 or deg <= -135:
                self.last_dir = "left"
            elif -135 < deg < -45:
                self.last_dir = "up"

        if moving and e.frame_count() % 7 == 0:
            try:
                from Entities.Particle import spawn_dust
                spawn_dust(self.x + self.w / 2, self.y + self.h, world, amount=1)
            except ImportError:
                pass

        if not self.current_item:
            if e.mouse_btnp(e.MOUSE_BUTTON_LEFT) and not self.is_punching:
                self.is_punching = True
                self.punch_timer = self.punch_duration
                self.hit_entities = []
                self.punch_angle = math.atan2(
                    e._global_mouse_pos[1] - (self.y + self.h / 2),
                    e._global_mouse_pos[0] - (self.x + self.w / 2),
                )

        if self.is_punching:
            self.punch_timer -= 1
            if self.world:
                for entity in self.world.entities:
                    if entity is self or not hasattr(entity, 'take_damage'):
                        continue
                    if not entity.is_living and not getattr(entity, 'blocking', False):
                        continue
                    dist = math.hypot(
                        entity.x + entity.w / 2 - self.x,
                        entity.y + entity.h / 2 - self.y,
                    )
                    if dist < 18 and entity not in self.hit_entities:
                        angle_to_entity = math.atan2(
                            entity.y + entity.h / 2 - (self.y + self.h / 2),
                            entity.x + entity.w / 2 - (self.x + self.w / 2),
                        )
                        angle_diff = (angle_to_entity - self.punch_angle + math.pi) % (2 * math.pi) - math.pi
                        if abs(angle_diff) < math.radians(90):
                            self.hit_entities.append(entity)
                            entity.take_damage(5, self.world)
                            if hasattr(e, 'active_camera'):
                                e.active_camera.shake(3, 2)
                                if getattr(entity, 'is_living', False):
                                    e.active_camera.flash((200, 220, 255), 25, 4)

            if self.punch_timer <= 0:
                self.is_punching = False

        super().update()

    def _add_to_storage(self, obj):
        from Entities.Item import Item
        from Items.Sword import Sword
        from Items.Crossbow import Crossbow
        if not isinstance(obj, Item):
            return False

        if isinstance(obj, Sword) and self.equipment[0] is None:
            self.equipment[0] = obj
            return True

        if isinstance(obj, Crossbow) and self.equipment[1] is None:
            self.equipment[1] = obj
            return True

        if obj.stackable:
            for i, slot in enumerate(self.items):
                if slot is not None and slot is not obj and slot.can_stack_with(obj):
                    space = slot.stack_space()
                    take = min(obj.quantity, space)
                    slot.quantity += take
                    obj.quantity -= take
                    if obj.quantity <= 0:
                        return True

        for i, slot in enumerate(self.items):
            if slot is None:
                self.items[i] = obj
                return True

        return False

    def _remove_item(self, item):
        for i, it in enumerate(self.equipment):
            if it is item:
                self.equipment[i] = None
                return
        for i, it in enumerate(self.items):
            if it is item:
                self.items[i] = None
                return
        for i, it in enumerate(self.crafting):
            if it is item:
                self.crafting[i] = None
                return

    def _sync_current_item(self):
        if self.equipment[0] is not None:
            self.current_item = self.equipment[0]
        elif self.equipment[1] is not None:
            self.current_item = self.equipment[1]
        else:
            self.current_item = None

    def _cycle_weapon(self):
        if self.equipment[0] is not None and self.equipment[1] is not None:
            self.equipment[0], self.equipment[1] = self.equipment[1], self.equipment[0]
            self._sync_current_item()
