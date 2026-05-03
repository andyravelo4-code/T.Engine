from Engine import engine as e 
from Entities.Object import Object

class Player(Object):
    def __init__(self, x, y, w, h,bank,image_x=0,image_y=0):
        super().__init__(x, y, w, h,bank)
        self.image_x=image_x
        self.image_y=image_y
        self.last_dir='left'
    def draw(self):
        e.blt(self.x,self.y+1,self.bank,3*8,8*8,8,8)
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
                self.animate(0,2,5,4)
                self.last_dir="up"
            case "down":
                self.animate(0,3,5,4)
                self.last_dir="down"  
            case "left":
                self.animate(0,1,5,4)
                self.last_dir='left'
            case "right":
                self.last_dir='right'
                self.animate(0,0,5,4)
        super().draw()
        self.current_item.draw()
    def update(self):
        self.direction="idle"
        self.current_item.update()
        if e.btn(e.KEY_W):
            self.direction="up"
            self.y-=self.speed
        if e.btn(e.KEY_S):
            self.direction="down"
            self.y+=self.speed
        if e.btn(e.KEY_A):
            self.direction="left"
            self.x-=self.speed
        if e.btn(e.KEY_D):
            self.direction="right"
            self.x+=self.speed
        super().update()
    