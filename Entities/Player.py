import math
import pygame

from Engine import engine as e
from Entities.Object import Object
from Entities.Npc import Npc


class Player(Object):
    MAX_ITEMS = 6

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
        self.items = [None] * self.MAX_ITEMS
        self.current_section = 0

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

        # e.circb(self.x+3.5,self.y+7.5,4,(255,255,255))
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
            
        # Draw health dot
        health_ratio = max(0, self.health / self.max_health)
        if health_ratio > 0.6:
            color = (95, 255, 129,60)  # Green
        elif health_ratio > 0.3:
            color = (255, 255, 0,60)  # Yellow
        else:
            color = (255, 0, 0,60)  # Red
            
        e.circb(int(self.x + self.w / 2), int(self.y-1.5), 2, color)
        
        # Draw punch arc
        if self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            alpha = int(255 * (1.0 - progress))
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)

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
                pygame.draw.polygon(surf, (255, 255, 255, alpha), points)

            e.graphics.screen.blit(surf, (self.x + self.w/2 - 16 + e.graphics._camera_x, self.y + self.h/2 - 16 + e.graphics._camera_y))

    def update(self):
        world = self.world
        self.direction = "idle"

        # Mise à jour de l'item tenu
        if self.current_item:
            self.current_item.update()

        # --- Logique d'inventaire ---
        # Ramasser (E)
        if e.btnp(e.KEY_E):
            from Entities.Item import Item

            slot = next((i for i, it in enumerate(self.items) if it is None), None)
            if slot is not None:
                for obj in list(world.entities):
                    if isinstance(obj, Item) and not obj.picked_up:
                        if self.is_collid(obj):
                            obj.picked_up = True
                            obj.parent = self
                            if hasattr(obj, "world"):
                                obj.world = world
                            self.items[slot] = obj
                            if not self.current_item:
                                self.current_item = obj
                            world.remove(obj)
                            break

        # Changer d'item (F)
        if e.btnp(e.KEY_F) and sum(1 for it in self.items if it) > 1:
            idx = next(i for i, it in enumerate(self.items) if it is self.current_item)
            for offset in range(1, 7):
                nxt = (idx + offset) % 6
                if self.items[nxt] is not None:
                    self.current_item = self.items[nxt]
                    self.current_section = 0 if nxt < 3 else 1
                    break

        # Sélection directe par chiffres 1-6
        for i in range(6):
            key = getattr(e, f"KEY_{i + 1}", None)
            if key and e.btnp(key) and self.items[i] is not None:
                self.current_item = self.items[i]
                self.current_section = 0 if i < 3 else 1

        # Lâcher l'item (R)
        if e.btnp(e.KEY_R) and self.current_item:
            item_to_drop = self.current_item
            item_to_drop.picked_up = False
            item_to_drop.parent = None
            item_to_drop.x = self.x
            item_to_drop.y = self.y

            world.add(item_to_drop)
            slot = self.items.index(item_to_drop)
            self.items[slot] = None
            self.current_item = next((it for it in self.items if it is not None), None)

        # --- Déplacement ---
        moving = False
        dx = 0
        dy = 0
        if e.btn(e.KEY_W) or e.btn(e.KEY_Z):
            self.direction = "up"
            dy -= self.speed
            self.last_dir = "up"
            moving = True
        if e.btn(e.KEY_S):
            self.direction = "down"
            dy += self.speed
            self.last_dir = "down"
            moving = True
        if e.btn(e.KEY_A) or e.btn(e.KEY_Q):
            self.direction = "left"
            dx -= self.speed
            self.last_dir = "left"
            moving = True
        if e.btn(e.KEY_D):
            self.direction = "right"
            dx += self.speed
            self.last_dir = "right"
            moving = True

        # Lunge effect during attack
        if not self.current_item and self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            # Quadratic ease-out speed
            lunge_speed = 3.5 * (1.0 - progress)
            dx += math.cos(self.punch_angle) * lunge_speed
            dy += math.sin(self.punch_angle) * lunge_speed
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
            # Quadratic ease-out speed
            lunge_speed = 3.5 * (1.0 - progress)
            dx += math.cos(slash_angle) * lunge_speed
            dy += math.sin(slash_angle) * lunge_speed
            moving = True

        # Move X and check collision
        if dx != 0:
            self.x += dx
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self and not isinstance(obj, Npc):
                    if self.is_collid(obj):
                        self.x -= dx
                        break

        # Move Y and check collision
        if dy != 0:
            self.y += dy
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self and not isinstance(obj, Npc):
                    if self.is_collid(obj):
                        self.y -= dy
                        break

        # Si on ne bouge pas, on regarde vers la souris
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
                
        # Unarmed punch logic
        if not self.current_item:
            if e.mouse_btnp(e.MOUSE_BUTTON_LEFT) and not self.is_punching:
                self.is_punching = True
                self.punch_timer = self.punch_duration
                self.hit_entities = []
                self.punch_angle = math.atan2(
                    e._global_mouse_pos[1] - (self.y + self.h/2),
                    e._global_mouse_pos[0] - (self.x + self.w/2)
                )

        if self.is_punching:
            self.punch_timer -= 1
            if self.world:
                for entity in self.world.entities:
                    if entity is self or not hasattr(entity, 'take_damage'):
                        continue
                    if not entity.is_living and not getattr(entity, 'blocking', False):
                        continue
                    dist = math.hypot(entity.x + entity.w/2 - self.x, entity.y + entity.h/2 - self.y)
                    if dist < 18 and entity not in self.hit_entities:
                            # check if the entity is within the punch angle sector
                            angle_to_entity = math.atan2(entity.y + entity.h/2 - (self.y + self.h/2), entity.x + entity.w/2 - (self.x + self.w/2))
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
