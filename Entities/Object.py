from Engine import engine as e


class Object:
    def __init__(self, x: int, y: int, w: int, h: int, bank, speed=1):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bank = bank
        self.direction = "idle"
        self.speed = speed
        self.items = []
        self.current_item = None
        # Whether this object blocks movement for pathfinding
        self.blocking = False
        self.is_living = False
        self.hitbox_inset = 0
        self.max_health = 100
        self.health = 100

    @property
    def hitbox(self):
        ins = self.hitbox_inset
        return (self.x + ins, self.y + ins, self.w - ins * 2, self.h - ins * 2)

    def is_collid(self, other):
        hx, hy, hw, hh = self.hitbox
        ox, oy, ow, oh = other.hitbox
        return hx < ox + ow and hx + hw > ox and hy < oy + oh and hy + hh > oy

    @property
    def get_center(self):
        return self.x + self.w / 2, self.y + self.h / 2

    def draw(self):
        pass

    def take_damage(self, amount, world):
        self.health -= amount
        died = self.health <= 0

        try:
            from Entities.Particle import spawn_blood, spawn_hit, spawn_bones
            if self.is_living:
                spawn_blood(self.x + self.w / 2, self.y + self.h / 2, world)
            else:
                spawn_hit(self.x + self.w / 2, self.y + self.h / 2, world, amount=3)
            if died:
                spawn_bones(self.x + self.w / 2, self.y + self.h / 2, world)
        except ImportError:
            pass

        if died:
            try:
                from Engine import engine
                if self.is_living and hasattr(engine, 'active_camera'):
                    engine.active_camera.flash((120, 255, 120), 35, 10)
            except ImportError:
                pass
            world.remove(self)

    def update(self):
        pass

    def draw_image(self, index_x, index_y, rotate=0, offset=(0, 0)):
        e.blt(
            self.x + offset[0],
            self.y + offset[1],
            self.bank,
            self.w * index_x,
            self.h * index_y,
            self.w,
            self.h,
            rotate=rotate,
        )

    def animate(self, index_x, index_y, intervall, nbr_frames):
        img_x = getattr(self, "image_x", 0)
        img_y = getattr(self, "image_y", 0)
        self.u = (img_x + index_x) * self.w + e.frame_count() // intervall % nbr_frames * self.w
        e.blt(
            round(self.x),
            round(self.y),
            self.bank,
            self.u,
            (img_y + index_y) * self.h,
            self.w,
            self.h,
            0,
        )
