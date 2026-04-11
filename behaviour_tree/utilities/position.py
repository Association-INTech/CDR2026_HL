import math

class Position:
    def __init__(self, x, y, angle):
        self.x=x
        self.y=y
        self.angle=angle
        
    def __str__(self):
        return f"Pos: x {self.x}, y {self.y}, a {self.angle}"
    
    def difference(self,pos):
        x=self.x-pos.x
        y=self.y-pos.y
        angle=(self.angle-pos.angle)%360
        return Position(x,y,angle)

    def add(self,pos):
        x=self.x+pos.x
        y=self.y+pos.y
        angle=(self.angle+pos.angle)%360
        return Position(x,y,angle)


    def foward(self,dist):
        x = self.x + dist*math.cos(math.radians(self.angle))
        y = self.y +dist*math.sin(math.radians(self.angle))
        return Position(x,y,self.angle)

    def distance(self,pos):
        return math.sqrt((pos.x-self.x)**2+(pos.y-self.y)**2)
