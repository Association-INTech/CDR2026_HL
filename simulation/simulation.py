import sys
import pygame
import random
import math
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from utilities.position import Position

class Rectangle:
    def __init__(self, x, y, width, height, color, angle=0, speed=0):
        self.pos = Position(x, y, angle)
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed  # pixels per second

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pos.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pos.y += self.speed * dt

    def clamp(self, width, height):
        """Keep rectangle within the surface"""
        self.pos.x = max(0, min(self.pos.x, width - self.width))
        self.pos.y = max(0, min(self.pos.y, height - self.height))

    def draw(self, surface):
        # Rotate the rectangle surface
        rotated_image = pygame.transform.rotate(self.image, self.pos.angle)
        rotated_rect = rotated_image.get_rect(center=(self.pos.x + self.width / 2, self.pos.y + self.height / 2))

        # Draw rotated rectangle on main surface
        surface.blit(rotated_image, rotated_rect.topleft)

class SimRobot():
    REF_WIDTH=310
    REF_HEIGHT=175
    
    def __init__(self, pos, color=(255, 0, 0), speed=250):        
        self.pos = Position(0,0,0)
        self.setCenterPos(pos)
        self.color = color
        self.speed = speed
        self.area_width = 3000
        self.area_height = 2000
                
        if self.pos.angle % 180 == 0:
            self.width, self.height = self.REF_HEIGHT, self.REF_WIDTH
        else:
            self.width, self.height = self.REF_WIDTH, self.REF_HEIGHT

        self.move_remaining = 0
        self.reverse = False
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def set_bounds(self, width, height):
        self.area_width = width
        self.area_height = height

    def clamp_to_bounds(self):
        self.pos.x = max(0, min(self.pos.x, self.area_width - self.width))
        self.pos.y = max(0, min(self.pos.y, self.area_height - self.height))
        
    def getCenterPos(self):
        if self.pos.angle == 0 or self.pos.angle == 180:
            self.width = self.REF_HEIGHT
            self.height = self.REF_WIDTH
        else:
            self.width = self.REF_WIDTH
            self.height = self.REF_HEIGHT

        center_x = self.pos.x + self.width // 2
        center_y = self.pos.y + self.height // 2
        return Position(center_x, center_y, self.pos.angle)

    def setCenterPos(self, centerPos):
        if centerPos.angle == 0 or centerPos.angle == 180:
            self.width = self.REF_HEIGHT
            self.height = self.REF_WIDTH
        else:
            self.width = self.REF_WIDTH
            self.height = self.REF_HEIGHT

        self.pos.x = centerPos.x - self.width // 2
        self.pos.y = centerPos.y - self.height // 2
        self.pos.angle = centerPos.angle

    def handle_input(self, dt, groupList=[]):
        keys = pygame.key.get_pressed()
        coef = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            coef = 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            coef = -1

        dx = coef * self.speed * dt * math.cos(math.radians(self.pos.angle))
        dy = coef * self.speed * dt * math.sin(math.radians(self.pos.angle))
        self.pos.x += dx
        self.pos.y += dy
        #self.clamp_to_bounds()

        collide = self.collidelistallNutBoxGroup(groupList)
        
        for i in collide:
            groupList[i].move(dx, dy)

    def start_move(self, distance):
        self.move_remaining = abs(distance)
        self.reverse = (distance < 0)
        

    def update_move(self, dt, groupList=[]):
        if self.move_remaining == 0:
            return

        speed = self.speed
        if self.reverse:
            speed = -speed
        
        step = speed * dt

        if abs(step) > abs(self.move_remaining):
            step = self.move_remaining

        dx = step * math.cos(math.radians(self.pos.angle))
        dy = step * math.sin(math.radians(self.pos.angle))

        self.pos.x += dx
        self.pos.y += dy
        #self.clamp_to_bounds()
        self.move_remaining -= abs(step)

        #print(f"Step: {step}")

        collide = self.collidelistallNutBoxGroup(groupList)
        for i in collide:
            groupList[i].move(dx, dy)

    def rotate(self, rotateAngle, groupList=[]):
        
        for i in self.listAllEaten(groupList):
            groupList[i].rotate(rotateAngle)
        
        center = self.getCenterPos()
        self.setCenterPos(center.add(Position(0, 0, rotateAngle)))

    def updateRect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

    def draw(self, surface):
        self.updateRect()
        pygame.draw.rect(surface, self.color, self.rect)

    def collidelistallNutBoxGroup(self, group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        return self.rect.collidelistall(rects)    
    
    def listAllEaten(self, group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        return self.rect.collidelistall(rects)


class SimRobotMagicoBus(SimRobot):    
    def __init__(self, pos, color=(255, 0, 0), speed=250):
        super().__init__(pos, color, speed)
        self.INS_WIDTH = 170
        self.isTopDown = True
        self.isBottomDown = True


    def updateRect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)        
        
        sideLength = (self.REF_WIDTH - self.INS_WIDTH) // 2
        thickness = 4  # thickness of the barriers

        if self.pos.angle == 0:
            self.rect       = pygame.Rect(self.pos.x, self.pos.y, self.REF_HEIGHT, self.REF_WIDTH)
            self.leftRect   = pygame.Rect(self.pos.x, self.pos.y, self.REF_HEIGHT, sideLength)
            self.rightRect  = pygame.Rect(self.pos.x, self.pos.y + sideLength + self.INS_WIDTH, self.REF_HEIGHT, sideLength)
            self.bottomRect = pygame.Rect(self.pos.x, self.pos.y + sideLength, thickness, self.INS_WIDTH)
            self.topRect    = pygame.Rect(self.pos.x + self.REF_HEIGHT, self.pos.y + sideLength, thickness, self.INS_WIDTH)
            
        elif self.pos.angle == 90:
            self.rect       = pygame.Rect(self.pos.x, self.pos.y, self.REF_WIDTH, self.REF_HEIGHT)
            self.leftRect   = pygame.Rect(self.pos.x, self.pos.y, sideLength, self.REF_HEIGHT)
            self.rightRect  = pygame.Rect(self.pos.x + sideLength + self.INS_WIDTH, self.pos.y, sideLength, self.REF_HEIGHT)
            self.bottomRect = pygame.Rect(self.pos.x + sideLength, self.pos.y, self.INS_WIDTH, thickness)
            self.topRect    = pygame.Rect(self.pos.x + sideLength, self.pos.y + self.REF_HEIGHT, self.INS_WIDTH, thickness)
                 
        elif self.pos.angle == 180:
            self.rect       = pygame.Rect(self.pos.x, self.pos.y, self.REF_HEIGHT, self.REF_WIDTH)
            self.leftRect   = pygame.Rect(self.pos.x, self.pos.y, self.REF_HEIGHT, sideLength)
            self.rightRect  = pygame.Rect(self.pos.x, self.pos.y + sideLength + self.INS_WIDTH, self.REF_HEIGHT, sideLength)
            self.bottomRect = pygame.Rect(self.pos.x + self.REF_HEIGHT, self.pos.y + sideLength, thickness, self.INS_WIDTH)
            self.topRect    = pygame.Rect(self.pos.x, self.pos.y + sideLength, thickness, self.INS_WIDTH)

        elif self.pos.angle == 270:
            self.rect       = pygame.Rect(self.pos.x, self.pos.y, self.REF_WIDTH, self.REF_HEIGHT)
            self.leftRect   = pygame.Rect(self.pos.x, self.pos.y, sideLength, self.REF_HEIGHT)
            self.rightRect  = pygame.Rect(self.pos.x + sideLength + self.INS_WIDTH, self.pos.y, sideLength, self.REF_HEIGHT)
            self.bottomRect = pygame.Rect(self.pos.x + sideLength, self.pos.y + self.REF_HEIGHT, self.INS_WIDTH, thickness)
            self.topRect    = pygame.Rect(self.pos.x + sideLength, self.pos.y, self.INS_WIDTH, thickness)
        else:
            raise ValueError(f"Unexpected angle: {self.pos.angle}")


    def draw(self, surface):
        self.updateRect()
        pygame.draw.rect(surface, self.color, self.leftRect)
        pygame.draw.rect(surface, self.color, self.rightRect)
        if self.isBottomDown: pygame.draw.rect(surface, self.color, self.bottomRect)
        if self.isTopDown: pygame.draw.rect(surface, self.color, self.topRect)

    def collidelistallNutBoxGroup(self, group):
        rects = [nutBox.rect() for nutBox in group]
        self.updateRect()
        collisions = list()
        collisions += self.leftRect.collidelistall(rects)
        collisions += self.rightRect.collidelistall(rects)
        if self.isBottomDown: collisions += self.bottomRect.collidelistall(rects)
        if self.isTopDown: collisions += self.topRect.collidelistall(rects)
        return list(set(collisions))
    
class SimRobotChasseNeige(SimRobot):
    REF_HEIGHT = 175
    REF_WIDTH = 310

    def __init__(self, pos, color=(255, 0, 0), speed=250):
        DISTANCE_CODEUSES=54
        self.distance_centre_codeuses = self.REF_HEIGHT/2-DISTANCE_CODEUSES
        super().__init__(pos, color, speed)

    def getCenterPos(self):
        center = super().getCenterPos()
        if self.pos.angle == 0:
            center.x -= self.distance_centre_codeuses
        elif self.pos.angle == 90:
            center.y -= self.distance_centre_codeuses
        elif self.pos.angle == 180:
            center.x += self.distance_centre_codeuses
        elif self.pos.angle == 270:
            center.y += self.distance_centre_codeuses
        return center
    
    def setCenterPos(self, centerPos):
        center = Position(centerPos.x, centerPos.y, centerPos.angle)
        if center.angle == 0:
            center.x += self.distance_centre_codeuses
        elif center.angle == 90:
            center.y += self.distance_centre_codeuses
        elif center.angle == 180:
            center.x -= self.distance_centre_codeuses
        elif center.angle == 270:
            center.y -= self.distance_centre_codeuses
        super().setCenterPos(center)
        

class NutBox(Rectangle):
    WIDTH = 150
    HEIGHT = 50
    def __init__(self, x, y, color, angle=0):
        super().__init__(x, y, NutBox.WIDTH, NutBox.HEIGHT, color, angle)

    def updateRect(self):
        if self.pos.angle % 180 == 0:
            self.rect = pygame.Rect(self.pos.x, self.pos.y, NutBox.WIDTH, NutBox.HEIGHT)
        else:
            self.rect = pygame.Rect(self.pos.x, self.pos.y, NutBox.HEIGHT, NutBox.WIDTH)

    def draw(self, surface):
        self.updateRect()
        pygame.draw.rect(surface, self.color, self.rect)

class NutBoxGroup():
    BOX_COUNT = 4
    def __init__(self, x, y, color1, color2, angle=0):
        self.pos = Position(x, y, angle)
        self.colors = [color1, color1, color2, color2]
        random.shuffle(self.colors)
        self.addNutBoxes(self.colors)
    
    def addNutBoxes(self, colors):
        self.nutBoxes = []
        for i in range(NutBoxGroup.BOX_COUNT):
            if self.pos.angle == 0:
                self.nutBoxes.append(NutBox(x=self.pos.x, y=self.pos.y + NutBox.HEIGHT * i, color=colors[i], angle=self.pos.angle))
            elif self.pos.angle == 90:
                self.nutBoxes.append(NutBox(x=self.pos.x + NutBox.HEIGHT * i, y=self.pos.y, color=colors[NutBoxGroup.BOX_COUNT - i - 1], angle=self.pos.angle))
            elif self.pos.angle == 180:
                self.nutBoxes.append(NutBox(x=self.pos.x, y=self.pos.y + NutBox.HEIGHT * i, color=colors[NutBoxGroup.BOX_COUNT - i - 1], angle=self.pos.angle))
            elif self.pos.angle == 270:
                self.nutBoxes.append(NutBox(x=self.pos.x + NutBox.HEIGHT * i, y=self.pos.y, color=colors[i], angle=self.pos.angle))
            else:
                raise ValueError(f"Unexpected angle: {self.pos.angle}")

    
    def rect(self):
        if self.pos.angle == 0 or self.pos.angle == 180:
            return pygame.Rect(self.pos.x, self.pos.y, NutBox.WIDTH, NutBox.HEIGHT * NutBoxGroup.BOX_COUNT)
        else:
            return pygame.Rect(self.pos.x, self.pos.y, NutBox.HEIGHT * NutBoxGroup.BOX_COUNT, NutBox.WIDTH)


    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy
        for nutBox in self.nutBoxes:
            nutBox.pos.x += dx
            nutBox.pos.y += dy
    
    def rotate(self, angle):
        self.pos.angle = (self.pos.angle + angle) % 360
        self.addNutBoxes(self.colors)

    def draw(self, surface):
        for nutBox in self.nutBoxes:
            nutBox.draw(surface)



class Simulation:
    def __init__(self, scale, robot, auto_start=True):
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
        
        #Fix path for background image
        background_path = Path(__file__).resolve().parent / "table.svg"
        self.background = pygame.image.load(str(background_path)).convert()

        self.blue = (0, 128, 255)
        self.yellow = (255, 128, 0)


        self.robot = robot
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
        self.dt = min(self.fps.tick(60) / 1000, 0.1)  # seconds per frame
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
                if event.key == pygame.K_f:
                    print(f"Robot pos: {self.robot.pos}")
                if event.key == pygame.K_r:
                    self.robot.rotate(90, groupList=self.nutBoxGroups)
                if event.key == pygame.K_t:
                    self.robot.isTopDown = not self.robot.isTopDown
                if event.key == pygame.K_b:
                    self.robot.isBottomDown = not self.robot.isBottomDown
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    mouse_x, mouse_y = event.pos
                    x = mouse_x / self.scale
                    y = mouse_y / self.scale
                    print(f"Clicked : x={x:.2f}, y={y:.2f}")

    def update(self):
        self.robot.handle_input(self.dt, self.nutBoxGroups)
        self.robot.update_move(self.dt, self.nutBoxGroups)


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
    robot = SimRobotChasseNeige(
        pos=Position(150, 100, 90),
        color=(255, 0, 0),
        speed=250,
    )
    simulation = Simulation(scale=0.5, robot=robot)