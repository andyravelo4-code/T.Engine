from Engine import engine as e 
from Entities.Object import Object

class Player(Object):
    def __init__(self, x, y, w, h,bank,image_x=0,image_y=0):
        super().__init__(x, y, w, h,bank)
        self.image_x=image_x
        self.image_y=image_y
        self.last_dir='left'
    def draw(self):
        e.blt(self.x,self.y+1,self.bank,3*8,6*8,8,8)
        match self.direction :
            case "idle":
                self.animate(self.bank,0,5 if self.last_dir=='left' else 4,5,4)
            case "up":
                self.animate(self.bank,0,2,5,4)
            case "down":
                self.animate(self.bank,0,3,5,4)
            case "left":
                self.animate(self.bank,0,1,5,4)
                self.last_dir='left'
            case "right":
                self.last_dir='right'
                self.animate(self.bank,0,0,5,4)
        return super().draw()
    def update(self):
        self.direction="idle"
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
        return super().update()
    