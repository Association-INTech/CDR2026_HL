import pygame
import random
import math

class Rectangle:
    def __init__(self, x, y, width, height, color, angle=0, speed=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed  # pixels per second
        self.angle = angle  # current rotation in degrees

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt

    def clamp(self, width, height):
        """Keep rectangle within the surface"""
        self.x = max(0, min(self.x, width - self.width))
        self.y = max(0, min(self.y, height - self.height))

    def draw(self, surface):
        # Rotate the rectangle surface
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))

        # Draw rotated rectangle on main surface
        surface.blit(rotated_image, rotated_rect.topleft)

class Robot():
    def __init__(self, x, y, color, angle=0, speed=250):
        self.x = x
        self.y = y
        self.color = color
        self.angle = angle
        self.speed = speed
        
        self.REF_WIDTH = 310
        self.REF_HEIGHT = 175
        
        if self.angle % 180 == 0:
            self.width, self.height = self.REF_HEIGHT, self.REF_WIDTH
        else:
            self.width, self.height = self.REF_WIDTH, self.REF_HEIGHT

        self.move_remaining = 0
        self.reverse = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def getCenterPos(self):
        if self.angle==0 or self.angle==180:
            self.width = self.REF_HEIGHT
            self.height = self.REF_WIDTH
        else:
            self.width = self.REF_WIDTH
            self.height = self.REF_HEIGHT

        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        return (center_x,center_y)


    def handle_input(self, dt, groupList=[]):
        keys = pygame.key.get_pressed()
        coef=0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            coef=1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            coef = -1

        dx=coef*self.speed * dt*math.cos(math.radians(self.angle))
        dy=coef*self.speed * dt*math.sin(math.radians(self.angle))
        self.x+=dx
        self.y+=dy

        collide = self.collidelistallNutBoxGroup(groupList)
        
        for i in collide:
            groupList[i].move(dx,dy)

    def start_move(self, distance):
        self.move_remaining = abs(distance)
        self.reverse=(distance<0)
        

    def update_move(self, dt, groupList=[]):
        if self.move_remaining == 0:
            return

        speed=self.speed
        if self.reverse:
            speed=-speed
        
        step = speed * dt

        if abs(step) > abs(self.move_remaining):
            step = self.move_remaining

        dx = step * math.cos(math.radians(self.angle))
        dy = step * math.sin(math.radians(self.angle))

        self.x += dx
        self.y += dy
        self.move_remaining -= abs(step)

        print(f"Step: {step}")

        collide = self.collidelistallNutBoxGroup(groupList)
        for i in collide:
            groupList[i].move(dx, dy)

    def rotate(self, rotateAngle,groupList=[]):
        
        for i in self.listAllEaten(groupList):
            groupList[i].rotate(rotateAngle)
        
        center_x,center_y = self.getCenterPos()
        
        self.angle=(self.angle+rotateAngle) % 360


        if rotateAngle % 180 != 0:
            self.width, self.height = self.height, self.width

        self.x = center_x - self.width//2
        self.y = center_y - self.height//2

        #print(f"{center_x},{center_y} => {self.getCenterPos()}")

    def updateRect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        self.updateRect()
        pygame.draw.rect(surface, self.color, self.rect)

    def collidelistallNutBoxGroup(self, group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        return self.rect.collidelistall(rects)    
    
    def listAllEaten(self,group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        return self.rect.collidelistall(rects)


class RobotMagicoBus(Robot):
    def __init__(self, x, y, color,angle=0, speed=250):
        super().__init__(x, y, color,angle, speed)
        self.INS_WIDTH = 170
        self.isTopDown=True
        self.isBottomDown=True


    def updateRect(self):
        self.rect=pygame.Rect(self.x,self.y,self.width,self.height)        
        
        sideLength=(self.REF_WIDTH-self.INS_WIDTH)//2
        thickness=4 #thickness of the barriers

        if self.angle==0:
            self.rect=pygame.Rect(self.x,self.y,self.REF_HEIGHT,self.REF_WIDTH)         
            self.leftRect=pygame.Rect(self.x,self.y,self.REF_HEIGHT,sideLength)        
            self.rightRect=pygame.Rect(self.x,self.y+sideLength+self.INS_WIDTH,self.REF_HEIGHT,sideLength)
            self.bottomRect=pygame.Rect(self.x,self.y+sideLength,thickness,self.INS_WIDTH)      
            self.topRect=pygame.Rect(self.x+self.REF_HEIGHT,self.y+sideLength,thickness,self.INS_WIDTH) 
            
        elif self.angle==90:
            self.rect=pygame.Rect(self.x,self.y,self.REF_WIDTH,self.REF_HEIGHT)         
            self.leftRect=pygame.Rect(self.x,self.y,sideLength,self.REF_HEIGHT)        
            self.rightRect=pygame.Rect(self.x+sideLength+self.INS_WIDTH,self.y,sideLength,self.REF_HEIGHT)
            self.bottomRect=pygame.Rect(self.x+sideLength,self.y,self.INS_WIDTH,thickness)      
            self.topRect=pygame.Rect(self.x+sideLength,self.y+self.REF_HEIGHT,self.INS_WIDTH,thickness)      
                 
        elif self.angle==180:
            self.rect=pygame.Rect(self.x,self.y,self.REF_HEIGHT,self.REF_WIDTH)         
            self.leftRect=pygame.Rect(self.x,self.y,self.REF_HEIGHT,sideLength)        
            self.rightRect=pygame.Rect(self.x,self.y+sideLength+self.INS_WIDTH,self.REF_HEIGHT,sideLength)
            self.bottomRect=pygame.Rect(self.x+self.REF_HEIGHT,self.y+sideLength,thickness,self.INS_WIDTH)      
            self.topRect=pygame.Rect(self.x,self.y+sideLength,thickness,self.INS_WIDTH)      

        elif self.angle==270:
            self.rect=pygame.Rect(self.x,self.y,self.REF_WIDTH,self.REF_HEIGHT)         
            self.leftRect=pygame.Rect(self.x,self.y,sideLength,self.REF_HEIGHT)        
            self.rightRect=pygame.Rect(self.x+sideLength+self.INS_WIDTH,self.y,sideLength,self.REF_HEIGHT)
            self.bottomRect=pygame.Rect(self.x+sideLength,self.y+self.REF_HEIGHT,self.INS_WIDTH,thickness)      
            self.topRect=pygame.Rect(self.x+sideLength,self.y,self.INS_WIDTH,thickness)      
        else:
            raise ValueError(f"Unexpected angle: {self.angle}")


    def draw(self, surface):
        self.updateRect()
        #pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.color, self.leftRect)
        pygame.draw.rect(surface, self.color, self.rightRect)
        if self.isBottomDown: pygame.draw.rect(surface, self.color, self.bottomRect)
        if self.isTopDown: pygame.draw.rect(surface, self.color, self.topRect)

    def collidelistallNutBoxGroup(self, group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        collisions= list()
        collisions+=self.leftRect.collidelistall(rects)
        collisions+=self.rightRect.collidelistall(rects)
        if self.isBottomDown: collisions+=self.bottomRect.collidelistall(rects)
        if self.isTopDown: collisions+=self.topRect.collidelistall(rects)
        return list(set(collisions))
    

class NutBox(Rectangle):
    WIDTH=150
    HEIGHT=50
    def __init__(self, x, y, color,angle=0):
        self.x = x
        self.y = y
        self.color = color
        self.angle=angle
        super().__init__(self.x,self.y,NutBox.WIDTH,NutBox.HEIGHT,self.color,self.angle)

    def updateRect(self):
        if self.angle%180==0:
            self.rect=pygame.Rect(self.x,self.y,NutBox.WIDTH,NutBox.HEIGHT)
        else:
            self.rect=pygame.Rect(self.x,self.y,NutBox.HEIGHT,NutBox.WIDTH)


    def draw(self, surface):
        self.updateRect()
        pygame.draw.rect(surface, self.color, self.rect)

class NutBoxGroup():
    BOX_COUNT=4
    def __init__(self, x, y, color1, color2, angle=0):
        self.x = x
        self.y = y
        self.angle=angle
        self.colors = [color1,color1,color2,color2]
        random.shuffle(self.colors)
        self.addNutBoxes(self.colors)
    
    def addNutBoxes(self,colors):
        self.nutBoxes = []
        for i in range(NutBoxGroup.BOX_COUNT):
            if self.angle==0:
                self.nutBoxes.append(NutBox(x=self.x, y=self.y+NutBox.HEIGHT*i, color=colors[i],angle=self.angle))
            elif self.angle==90:
                self.nutBoxes.append(NutBox(x=self.x+NutBox.HEIGHT*i, y=self.y, color=colors[NutBoxGroup.BOX_COUNT-i-1],angle=self.angle))
            elif self.angle==180:
                self.nutBoxes.append(NutBox(x=self.x, y=self.y+NutBox.HEIGHT*i, color=colors[NutBoxGroup.BOX_COUNT-i-1],angle=self.angle))
            elif self.angle==270:
                self.nutBoxes.append(NutBox(x=self.x+NutBox.HEIGHT*i, y=self.y, color=colors[i],angle=self.angle))
            else:
                raise ValueError(f"Unexpected angle: {self.angle}")

    
    def rect(self):
        if self.angle==0 or self.angle==180:
            return pygame.Rect(self.x,self.y,NutBox.WIDTH,NutBox.HEIGHT*NutBoxGroup.BOX_COUNT)
        else:
            return pygame.Rect(self.x,self.y,NutBox.HEIGHT*NutBoxGroup.BOX_COUNT,NutBox.WIDTH)


    def move(self,dx,dy):
        self.x+=dx
        self.y+=dy
        for nutBox in self.nutBoxes:
            nutBox.x+=dx
            nutBox.y+=dy
    
    def rotate(self,angle):
        self.angle=(self.angle+angle)%360
        self.addNutBoxes(self.colors)

    def draw(self, surface):
        for nutBox in self.nutBoxes:
            nutBox.draw(surface)



class Simulation:
    def __init__(self, scale, auto_start=True):
        self.running = True
        self.width = 3000
        self.height = 2000
        self.scale = scale

        pygame.init()
        pygame.display.set_caption("Simulation debug")
        self.window = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
        self.surface = pygame.surface.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))
        self.fps = pygame.time.Clock()
        self.dt = self.fps.tick(60) / 1000  # seconds per frame

        pygame.font.init()
        self.font = pygame.font.SysFont("notomono", 30)
        self.background = pygame.image.load("table.svg").convert()

        self.blue=(0, 128, 255)
        self.yellow=(255, 128, 0)


        self.robot = Robot(
            x=150,
            y=100,
            color=(255, 0, 0),
            speed=250,
            angle=90  
        )
        '''
        self.nutBoxes = [
            NutBox(x=100, y=700, color=self.blue),
            NutBox(x=100, y=750, color=self.yellow),
            NutBox(x=100, y=800, color=self.blue),
            NutBox(x=100, y=850, color=self.yellow),

            NutBox(x=100, y=1500, color=self.blue),
            NutBox(x=100, y=1550, color=self.yellow),
            NutBox(x=100, y=1600, color=self.blue),
            NutBox(x=100, y=1650, color=self.yellow),

            NutBox(x=1050, y=1125, color=self.blue, angle=90),
            NutBox(x=1100, y=1125, color=self.yellow, angle=90),
            NutBox(x=1150, y=1125, color=self.blue, angle=90),
            NutBox(x=1200, y=1125, color=self.yellow, angle=90),

            NutBox(x=1000, y=1750, color=self.blue, angle=90),
            NutBox(x=1050, y=1750, color=self.yellow, angle=90),
            NutBox(x=1100, y=1750, color=self.blue, angle=90),
            NutBox(x=1150, y=1750, color=self.yellow, angle=90),

            NutBox(x=2750, y=700, color=self.blue),
            NutBox(x=2750, y=750, color=self.yellow),
            NutBox(x=2750, y=800, color=self.blue),
            NutBox(x=2750, y=850, color=self.yellow),

            NutBox(x=2750, y=1500, color=self.blue),
            NutBox(x=2750, y=1550, color=self.yellow),
            NutBox(x=2750, y=1600, color=self.blue),
            NutBox(x=2750, y=1650, color=self.yellow),

            NutBox(x=1900, y=1125, color=self.blue, angle=90),
            NutBox(x=1850, y=1125, color=self.yellow, angle=90),
            NutBox(x=1800, y=1125, color=self.blue, angle=90),
            NutBox(x=1750, y=1125, color=self.yellow, angle=90),

            NutBox(x=1950, y=1750, color=self.blue, angle=90),
            NutBox(x=1900, y=1750, color=self.yellow, angle=90),
            NutBox(x=1850, y=1750, color=self.blue, angle=90),
            NutBox(x=1800, y=1750, color=self.yellow, angle=90),
        ]
        '''
        self.nutBoxGroups = [
            NutBoxGroup(100, 700, self.blue, self.yellow),
            NutBoxGroup(100, 1500, self.blue, self.yellow),

            NutBoxGroup(1050, 1125, self.blue, self.yellow, angle=90),
            NutBoxGroup(1000, 1750, self.blue, self.yellow, angle=90),

            NutBoxGroup(2750, 700, self.blue, self.yellow),
            NutBoxGroup(2750, 1500, self.blue, self.yellow),

            NutBoxGroup(1750, 1125, self.blue, self.yellow, angle=90),
            NutBoxGroup(1800, 1750, self.blue, self.yellow, angle=90),
        ]
        
        self.forbidden_zones = []

        if auto_start:
            self.loop()

    def tick(self):
        # One frame - returns control immediately
        self.dt = min(self.fps.tick(60) / 1000,0.1)  # seconds per frame
        self.events()
        self.update()
        self.render()
        return self.running

    def loop(self):
        while self.running:
            self.events()
            self.update()
            self.render()
            self.dt = self.fps.tick(60) / 1000  # delta time (s)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # When "F" is pressed, print rectangle position
                if event.key == pygame.K_f:
                    print(f"Robot pos: x={self.robot.x:.1f}, y={self.robot.y:.1f}, angle={self.robot.angle}")
                if event.key == pygame.K_r:
                    self.robot.rotate(90,groupList=self.nutBoxGroups)
                if event.key == pygame.K_t:
                    self.robot.isTopDown= not self.robot.isTopDown
                if event.key == pygame.K_b:
                    self.robot.isBottomDown= not self.robot.isBottomDown


    def update(self):
        self.robot.handle_input(self.dt,self.nutBoxGroups)
        self.robot.update_move(self.dt, self.nutBoxGroups)
        #self.robot.clamp(self.width, self.height)

        #self.nutBox1.handle_input(self.dt)
        #self.nutBox1.clamp(self.width, self.height)


    def render(self):
        # Draw background
        self.surface.blit(pygame.transform.scale(self.background, self.surface.get_size()), (0, 0))

        transparent_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        for zone in self.forbidden_zones:
            if zone is not None:
                xmin, xmax, ymin, ymax, *_ = zone
                rect = pygame.Rect(xmin, ymin, xmax - xmin, ymax - ymin)
                pygame.draw.rect(transparent_surface, (255, 0, 0, 60), rect)  
        self.surface.blit(transparent_surface, (0, 0))
        """
        for nutBox in self.nutBoxes:
            nutBox.draw(self.surface)
        """
        for nutBoxGroup in self.nutBoxGroups:
            nutBoxGroup.draw(self.surface)

        self.robot.draw(self.surface)

        # Scale surface to window
        self.window.blit(pygame.transform.scale_by(self.surface, self.scale), (0, 0))
        pygame.display.update()


if __name__ == "__main__":
    simulation = Simulation(0.5)
