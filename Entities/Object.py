from Engine import engine as e

class Object:
    def __init__(self,x,y,w,h,bank,speed=1):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.bank=bank
        self.direction="idle"
        self.speed=speed
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def animate(self,bank,index_x,index_y,intervall,nbr_frames):
        self.u = index_x*self.w + e.frame_count() // intervall % nbr_frames * self.w
        e.blt(round(self.x),round(self.y),bank,self.u,index_y*self.h,self.w,self.h,0)