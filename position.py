import math

class Position:
    def __init__(self, x, y, angle):
        self.x=x
        self.y=y
        self.angle=angle
    
    def difference(self,pos):
        x=self.x-pos.x
        y=self.y-pos.y
        angle=self.angle-pos.angle
        return Position(x,y,angle)


    def foward(self,dist):
        self.x +=dist*math.cos(math.radians(self.angle))
        self.y +=dist*math.sin(math.radians(self.angle))
