from behaviour_tree.utilities.position import Position
#from communication import Comm
from behaviour_tree.utilities.communication import CommSim as Comm
import logging
import py_trees
import time
from behaviour_tree.utilities.graph import GridGraph
from behaviour_tree.utilities.logging_setup import setup_logging

AREA_WIDTH = 3000
AREA_HEIGHT = 2000


class Robot:
    "Gère toutes les actions tout relatif au robot"
    WIDTH=310
    HEIGHT=175

    
    def __init__(self, pos, simRobot=None):
        setup_logging()
        self.pos=pos
        self.comm=Comm(simRobot)
        self.actions=[]
        self.__countID=0 #variable de classe pour avoir un id
        self.start_time = time.time()
        self.logger = logging.getLogger("Robot")
        self.graph=GridGraph(AREA_WIDTH,AREA_HEIGHT,scale=10, rotate_buffer=Robot.HEIGHT//2)
        self.comm.link_frobidden(self.graph.forbidden)
        self.graph.addForbidden(600-Robot.WIDTH//2,2400+Robot.WIDTH//2,0,450+Robot.WIDTH//2) #forbidden zone pamis
        
        self.noisettes = [
            NutBox(Position(100, 700, 90)),     #0
            NutBox(Position(100, 1500, 90)),    #1
            NutBox(Position(1050, 1125, 0)),    #2
            NutBox(Position(1000, 1750, 0)),    #3
            NutBox(Position(1800, 1750, 0)),    #4
            NutBox(Position(1750, 1125, 0)),    #5
            NutBox(Position(2750, 1500, 90)),   #6
            NutBox(Position(2750, 700, 90))     #7
        ]        
        self.nutBoxGroupForbidden()
    
        
        self.pantries = [
            Position(100, 1200, 90),
            Position(800, 1200, 0),
            Position(1500, 1200, 0),
            Position(2200, 1200, 0),
            Position(2900, 1200, 90),
            Position(2300, 1900, 0),
            Position(1500, 1900, 0),
            Position(700, 1900, 0),
            Position(1250, 550, 0),
            Position(1750, 550, 0)

        ]
    
    def startBT(self, root, robot):
        behaviour_tree = py_trees.trees.BehaviourTree(root=root)
        self.logger.debug(py_trees.display.unicode_tree(root=root))
        behaviour_tree.setup(timeout=15)


        def post_tick_handler(tree: py_trees.trees.BehaviourTree) -> None:
            """Print tree and check for completion."""
            self.logger.debug(py_trees.display.unicode_tree(root=tree.root, show_status=True))
            
            if tree.root.status in [py_trees.common.Status.SUCCESS, py_trees.common.Status.FAILURE]:
                self.logger.debug(f"Finished | Status: {tree.root.status}")
                raise SystemExit                
        py_trees.logging.level = py_trees.logging.Level.DEBUG

        try:
            behaviour_tree.tick_tock(
                period_ms=100,
                number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
                pre_tick_handler=robot.comm.tick_simulation,
                post_tick_handler=post_tick_handler
            )
        except KeyboardInterrupt:
            behaviour_tree.interrupt()
    
    def nutBoxGroupForbidden(self):
        for noisette in self.noisettes:
            xmin,xmax,ymin,ymax=noisette.getForbiddenZone(buffer=Robot.WIDTH//2+10)
            noisette.index=self.graph.addForbidden(xmin,xmax,ymin,ymax)

    def getNutBoxPos(self):
        self.update()
        return self.pos.foward(Robot.HEIGHT//2) 

    def getID(self):
        self.__countID+=1
        return self.__countID

    def getPos(self):
        self.update()
        return self.pos
    
    def update(self):
        self.pos=self.comm.get_position()
        self.logger.debug(str(self.pos))
        for id in self.actions:
            if self.comm.get_feedback(id):
                self.actions.remove(id)

    def start_move(self,dist):
        id=self.getID()
        self.update()
        self.comm.start_move(dist)
        self.actions.append(id)
        return id

    def start_rotate(self, angle):
        id=self.getID()
        self.update()
        self.comm.start_rotate(angle)
        self.actions.append(id)
        return id
    
    def top_barrier(self,state):
        id=self.getID()
        self.comm.putTopBarrier(state)
        return id


    def bottom_barrier(self,state):
        id=self.getID()
        self.comm.putBottomBarrier(state)
        return id


    def is_moving(self):
        self.update()
        return len(self.actions)!=0 #check if actions empty

class robotChasseNeige(Robot):
    def __init__(self, pos, simRobot=None):
        super().__init__(pos, simRobot)
        
    def getNutBoxPos(self):
        self.update()
        return self.pos.foward(Robot.HEIGHT//2)

class robotMagicoBus(Robot):
    def __init__(self, pos, simRobot=None):
        super().__init__(pos, simRobot)
        
    def getNutBoxPos(self):
        self.update()
        contact = self.pos.foward(-Robot.HEIGHT//2) 
        if self.pos.angle == 0:
            return Position(contact.x, contact.y - NutBox.HEIGHT//2, 0)
        elif self.pos.angle == 90:
            return Position(contact.x - NutBox.HEIGHT//2, contact.y, 90)
        elif self.pos.angle == 180:
            return Position(contact.x, contact.y - NutBox.HEIGHT//2, 180)
        elif self.pos.angle == 270:
            return Position(contact.x - NutBox.HEIGHT//2, contact.y, 270)
        else:
            raise ValueError(f"Unexpected angle: {self.pos.angle}")



class NutBox():
    WIDTH=150
    HEIGHT=50
    BOX_COUNT=4
    def __init__(self,pos,push_pos=None):
        self.pos=pos #top right pos
        self.index=None
        self.push_pos = push_pos
        self.children = []
            
    def setCenter(self,pos):
        if pos.angle%180==0:
            self.pos=pos.add(Position(NutBox.WIDTH//2,-(NutBox.HEIGHT*NutBox.BOX_COUNT)//2,0))
        else:
            self.pos=pos.add(Position((NutBox.HEIGHT*NutBox.BOX_COUNT)//2,-NutBox.WIDTH//2,0))

    
    def getPushpos(self,buffer=0):
        if self.push_pos is not None:
            return self.push_pos.foward(-buffer)
        if self.pos.angle==0:
            return self.pos.add(Position(-buffer,NutBox.WIDTH//2,0))
        else:
            return self.pos.add(Position(NutBox.WIDTH//2,buffer,0))    
                
    def getForbiddenZone(self,buffer):
        if self.pos.angle% 180==0:
            sizex=200
            sizey=150
        else:
            sizex=150
            sizey=200
        return (
            int(self.pos.x - buffer),
            int(self.pos.x + sizex + buffer),
            int(self.pos.y - buffer),
            int(self.pos.y + sizey + buffer)
        )        

