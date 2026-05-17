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
        self.max_health = 100
        self.health = 100

    def is_collid(self, other):
        """Vérifie la collision entre cet objet et un autre."""
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )

    @property
    def get_center(self):
        return self.x + self.w / 2, self.y + self.h / 2

    def draw(self):
        pass

    def take_damage(self, amount, world):
        self.health -= amount
        
        # We spawn blood when hit
        try:
            from Entities.Particle import spawn_blood
            spawn_blood(self.x + self.w / 2, self.y + self.h / 2, world)
        except ImportError:
            pass

        if self.health <= 0:
            if hasattr(self, 'current_item') and self.current_item:
                # Drop items maybe?
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
        self.u = index_x * self.w + e.frame_count() // intervall % nbr_frames * self.w
        e.blt(
            round(self.x),
            round(self.y),
            self.bank,
            self.u,
            index_y * self.h,
            self.w,
            self.h,
            0,
        )
