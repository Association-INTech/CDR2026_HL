import math

class Position:
    def __init__(self, x, y, angle):
        self.x=x
        self.y=y
        self.angle=angle
    
    def foward(self,dist):
        self.x +=dist*math.cos(math.radians(self.angle))
        self.y +=dist*math.sin(math.radians(self.angle))
