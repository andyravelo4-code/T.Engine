from Engine import engine as e

class Object:
    def __init__(self,x:int,y:int,w:int,h:int,bank,speed=1):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.bank=bank
        self.direction="idle"
        self.speed=speed
        self.items=[]
        self.current_item=None
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def draw_image(self,index_x,index_y,rotate=0,offset=(0,0)):
        e.blt(self.x+offset[0],self.y+offset[1],self.bank,self.w*index_x,self.h*index_y,self.w,self.h,rotate=rotate)
    def animate(self,index_x,index_y,intervall,nbr_frames):
        self.u = index_x*self.w + e.frame_count() // intervall % nbr_frames * self.w
        e.blt(round(self.x),round(self.y),self.bank,self.u,index_y*self.h,self.w,self.h,0)