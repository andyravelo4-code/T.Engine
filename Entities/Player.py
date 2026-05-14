from Engine import engine as e 
from Entities.Object import Object
import math

class Player(Object):
    def __init__(self, x, y, w, h,bank,image_x=0,image_y=0):
        super().__init__(x, y, w, h,bank)
        self.image_x=image_x
        self.image_y=image_y
        self.last_dir='left'
    def draw(self):
        e.blt(self.x,self.y+1,self.bank,4*8,0*8,8,8)
        #e.circb(self.x+3.5,self.y+7.5,4,(255,255,255))
        last_dir_dict = {
            "up":6,
            "down":7,
            "left":5,
            "right":4
        }
        match self.direction :
            case "idle":
                self.animate(0,last_dir_dict[self.last_dir],5,4)
            case "up":
                self.animate(0,2,6,4)
                self.last_dir="up"
            case "down":
                self.animate(0,3,6,4)
                self.last_dir="down"  
            case "left":
                self.animate(0,1,6,4)
                self.last_dir='left'
            case "right":
                self.last_dir='right'
                self.animate(0,0,6,4)
        super().draw()
        if self.current_item:
            self.current_item.draw()
    def update(self, world):
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
                        if hasattr(obj, 'world'):
                            obj.world = world
                        self.items.append(obj)
                        if not self.current_item:
                            self.current_item = obj
                        world.remove(obj)
                        break

        # Changer d'item (Q)
        if e.btnp(e.KEY_Q) and len(self.items) > 1:
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
        if e.btn(e.KEY_W):
            self.direction="up"
            self.y-=self.speed
            self.last_dir="up"
            moving = True
        if e.btn(e.KEY_S):
            self.direction="down"
            self.y+=self.speed
            self.last_dir="down"
            moving = True
        if e.btn(e.KEY_A):
            self.direction="left"
            self.x-=self.speed
            self.last_dir='left'
            moving = True
        if e.btn(e.KEY_D):
            self.direction="right"
            self.x+=self.speed
            self.last_dir='right'
            moving = True
            
        # Si on ne bouge pas, on regarde vers la souris
        if not moving:
            mouse_angle = math.atan2(e._global_mouse_pos[1] - self.y, 
                                    e._global_mouse_pos[0] - self.x)
            deg = math.degrees(mouse_angle)
            
            if -45 <= deg <= 45:
                self.last_dir = "right"
            elif 45 < deg <= 135:
                self.last_dir = "down"
            elif deg > 135 or deg <= -135:
                self.last_dir = "left"
            elif -135 < deg < -45:
                self.last_dir = "up"
                
        super().update()
    