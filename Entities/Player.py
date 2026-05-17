import math

from Engine import engine as e
from Entities.Object import Object


class Player(Object):
    def __init__(self, x, y, w, h, bank, world=None, image_x=0, image_y=0):
        super().__init__(x, y, w, h, bank)
        self.world = world
        self.image_x = image_x
        self.image_y = image_y
        self.last_dir = "left"
        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 10
        self.punch_angle = 0
        self.hit_entities = []

    def draw(self):
        e.blt(
            self.x,
            self.y + 1,
            self.bank,
            4 * 8,
            0 * 8,
            8,
            8,
        )

        # e.circb(self.x+3.5,self.y+7.5,4,(255,255,255))
        last_dir_dict = {"up": 6, "down": 7, "left": 5, "right": 4}
        match self.direction:
            case "idle":
                self.animate(0, last_dir_dict[self.last_dir], 5, 4)
            case "up":
                self.animate(0, 2, 6, 4)
                self.last_dir = "up"
            case "down":
                self.animate(0, 3, 6, 4)
                self.last_dir = "down"
            case "left":
                self.animate(0, 1, 6, 4)
                self.last_dir = "left"
            case "right":
                self.last_dir = "right"
                self.animate(0, 0, 6, 4)
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
            
        e.circ(int(self.x + self.w / 2), int(self.y-3), 1, color)
        
        # Draw punch arc
        if self.is_punching:
            progress = 1.0 - (self.punch_timer / self.punch_duration)
            alpha = int(255 * (1.0 - progress))
            import pygame
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            
            center = (16, 16)
            radius = 8 + progress * 4
            points = []
            for i in range(-40, 41, 15):
                rad = math.radians(i) + self.punch_angle
                px = center[0] + math.cos(rad) * radius
                py = center[1] + math.sin(rad) * radius
                points.append((px, py))
            
            if len(points) >= 2:
                pygame.draw.lines(surf, (255, 255, 255, alpha),False, points, 2)
            
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

            for obj in list(world.entities):
                if isinstance(obj, Item) and not obj.picked_up:
                    if self.is_collid(obj):
                        obj.picked_up = True
                        obj.parent = self
                        # Donner la référence du monde aux armes (pour les flèches)
                        if hasattr(obj, "world"):
                            obj.world = world
                        self.items.append(obj)
                        if not self.current_item:
                            self.current_item = obj
                        world.remove(obj)
                        break

        # Changer d'item (Q)
        if e.btnp(e.KEY_F) and len(self.items) > 1:
            idx = self.items.index(self.current_item)
            self.current_item = self.items[(idx + 1) % len(self.items)]

        # Lâcher l'item (R)
        if e.btnp(e.KEY_R) and self.current_item:
            item_to_drop = self.current_item
            item_to_drop.picked_up = False
            item_to_drop.parent = None
            item_to_drop.x = self.x
            item_to_drop.y = self.y

            world.add(item_to_drop)
            self.items.remove(item_to_drop)
            self.current_item = self.items[0] if self.items else None

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

        # Move X and check collision
        if dx != 0:
            self.x += dx
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self:
                    if self.is_collid(obj):
                        self.x -= dx
                        break

        # Move Y and check collision
        if dy != 0:
            self.y += dy
            for obj in world.entities:
                if getattr(obj, "blocking", False) and obj != self:
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

        if moving and e.frame_count() % 5 == 0:
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
                    if entity != self and hasattr(entity, 'take_damage'):
                        dist = math.hypot(entity.x + entity.w/2 - self.x, entity.y + entity.h/2 - self.y)
                        if dist < 18 and entity not in self.hit_entities:
                            # check if the entity is within the punch angle sector
                            angle_to_entity = math.atan2(entity.y + entity.h/2 - (self.y + self.h/2), entity.x + entity.w/2 - (self.x + self.w/2))
                            angle_diff = (angle_to_entity - self.punch_angle + math.pi) % (2 * math.pi) - math.pi
                            if abs(angle_diff) < math.radians(90):
                                self.hit_entities.append(entity)
                                entity.take_damage(5, self.world)
                                try:
                                    from Entities.Particle import spawn_hit
                                    spawn_hit(entity.x, entity.y, self.world, amount=3)
                                    if hasattr(e, 'active_camera'):
                                        e.active_camera.shake(3, 2)
                                except Exception:
                                    pass

            if self.punch_timer <= 0:
                self.is_punching = False

        super().update()
