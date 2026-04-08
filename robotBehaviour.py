import random
import py_trees
import time

from position import Position
#from communication import Comm
from communication import CommSim as Comm

from graph import GridGraph

AREA_WIDTH = 3000
AREA_HEIGHT = 2000


class Robot:
    "Gère toutes les actions tout relatif au robot"
    WIDTH=310
    HEIGHT=175

    
    def __init__(self, pos):
        self.pos=pos
        self.comm=Comm()
        self.actions=[]
        self.__countID=0 #variable de classe pour avoir un id
        self.start_time = time.time()
        self.logger = py_trees.logging.Logger("Robot")
        self.graph=GridGraph(AREA_WIDTH,AREA_HEIGHT,scale=10)
        self.comm.link_frobidden(self.graph.forbidden)
        self.graph.addForbidden(600-Robot.WIDTH//2,2400+Robot.WIDTH//2,0,450+Robot.WIDTH//2) #forbidden zone pamis
        
        self.noisettes = [
            NutBox(Position(100, 700, 90)),
            NutBox(Position(100, 1500, 90)),
            NutBox(Position(1050, 1125, 0)),
            NutBox(Position(1000, 1750, 0)),
            NutBox(Position(1750, 1125, 0)),
            NutBox(Position(1800, 1750, 0)),
            NutBox(Position(2750, 700, 90)),
            NutBox(Position(2750, 1500, 90))
        ]        
        self.nutBoxGroupForbidden()
    
        self.noisettes[0].push_pos=self.noisettes[0].getPushpos().add(Position(0,NutBox.HEIGHT*NutBox.BOX_COUNT,180))
        self.noisettes[1].push_pos=self.noisettes[1].getPushpos().add(Position(0,NutBox.HEIGHT*NutBox.BOX_COUNT,180))
        
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
            
    
    def nutBoxGroupForbidden(self):
        for noisette in self.noisettes:
            xmin,xmax,ymin,ymax=noisette.getForbiddenZone(buffer=Robot.WIDTH//2)
            noisette.index=self.graph.addForbidden(xmin,xmax,ymin,ymax)

    def getNutBoxPosMagicoBus(self):
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
    def getNutBoxPosChasseNeige(self):
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

class NutBox():
    WIDTH=150
    HEIGHT=50
    BOX_COUNT=4
    def __init__(self,pos,push_pos=None):
        self.pos=pos #top right pos
        self.index=None
        self.push_pos = push_pos
    
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

class GetLoc(py_trees.behaviour.Behaviour):
    """Obtient le prochain endroit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="GetLoc")
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.WRITE)
        self.queue = []
        self.queue.append(Position(0,0,0))

    def update(self):
        if len(self.queue)==0:
            return py_trees.common.Status.FAILURE
        self.blackboard.loc=self.getNextLoc()
        self.logger.debug(f"Going to {str(self.blackboard.loc)}")
        return py_trees.common.Status.SUCCESS
    
    def getNextLoc(self):
        return self.queue.pop(0)


class GoToLoc(py_trees.decorators.PassThrough):
    """Va à l'endroit choisi"""

    def __init__(self, name: str):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.blackboard = self.attach_blackboard_client(name="GoToLoc")
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="plan", access=py_trees.common.Access.WRITE)

    def initialise(self):
        self.main_sequence.remove_all_children()
        self.createPlanGraph()
        #self.current_child=self.children[0]

    def createPlan(self):
        steps = []
        stepsBT = []

        currentPos = robot.getPos()
        dx = self.blackboard.loc.x - currentPos.x
        dy = self.blackboard.loc.y - currentPos.y

        def addStep(step_class, value):
            steps.append((step_class.__name__, value))
            stepsBT.append(step_class(
                name=f"{step_class.__name__}_{value}",
                value=value
            ))

        target_angle = 90 if dy > 0 else -90
        distance = abs(dy)

        rotate = target_angle - currentPos.angle
        rotate = (rotate + 180) % 360 - 180

        if rotate != 0:
            addStep(Rotate, rotate)
            currentPos.angle = target_angle

        addStep(Move, distance)

        target_angle = 0 if dx > 0 else 180
        distance = abs(dx)

        rotate = target_angle - currentPos.angle
        rotate = (rotate + 180) % 360 - 180

        if rotate != 0:
            addStep(Rotate, rotate)
            currentPos.angle = target_angle

        addStep(Move, distance)
        
        target_angle=self.blackboard.loc.angle
        rotate = target_angle - currentPos.angle
        rotate = (rotate + 180) % 360 - 180

        if rotate != 0:
            addStep(Rotate, rotate)
            currentPos.angle = target_angle

        self.blackboard.plan = steps
        self.main_sequence.add_children(stepsBT)      

    def createPlanGraph(self):
        steps = []
        stepsBT = []

        currentPos = robot.getPos()
        targetPos = Position(self.blackboard.loc.x,self.blackboard.loc.y,self.blackboard.loc.angle)

        def addStep(step_class, value):
            steps.append((step_class.__name__, value))
            stepsBT.append(step_class(
                name=f"{step_class.__name__}_{value}",
                value=value
            ))
        
        def getStep(posA,posB):
            diff=posB.difference(posA)
            if (diff.y==0 and diff.angle==0):
                return (Move,abs(diff.x))
            elif (diff.x==0 and diff.angle==0):
                return (Move,abs(diff.y))
            elif (diff.x==0 and diff.y==0):
                return (Rotate,diff.angle)

        path=robot.graph.getShortestPathPos(currentPos,targetPos)

        raw_steps = []
        prev_class =  None
        total_value = 0
        for i in range(len(path)-1):
            step,value=getStep(path[i],path[i+1])
            raw_steps.append((step,value))

            if prev_class==step:
                total_value+=value
            else:
                if prev_class is not None:
                    addStep(prev_class,total_value)
                prev_class=step
                total_value=value

        if prev_class is not None:
            addStep(prev_class,total_value)
        
        self.blackboard.plan = steps
        self.main_sequence.add_children(stepsBT)      


class Rotate(py_trees.behaviour.Behaviour):
    """Rotate robot by a given angle"""

    def __init__(self, name: str, value: float) -> None:
        super().__init__(name)
        self.angle = value

    def initialise(self):
        self.start_time=time.time()
        self.id=robot.start_rotate(self.angle)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS        
               
class Move(py_trees.behaviour.Behaviour):
    """Move robot forward by a given distance"""

    def __init__(self, name: str, value: float) -> None:
        super().__init__(name)
        self.distance = value

    def initialise(self):
        self.start_time=time.time()
        self.id=robot.start_move(self.distance)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class TopBarrier(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, state: bool) -> None:
        super().__init__(name)
        self.state = state

    def initialise(self):
        self.start_time=time.time()
        self.id=robot.top_barrier(self.state)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class BottomBarrier(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, state: bool) -> None:
        super().__init__(name)
        self.state = state

    def initialise(self):
        self.start_time=time.time()
        self.id=robot.bottom_barrier(self.state)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class ProcedureChasseNeige(py_trees.decorators.PassThrough):
    def __init__(self, name: str,):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetClosestNoisette(name="get_Noisette_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette"))
        self.main_sequence.add_child(TopBarrier(name="lift_top",state=False))
        self.main_sequence.add_child(BottomBarrier(name="drop_bot",state=True))
        self.main_sequence.add_child(Move(name="push_noisette",value=200))
        self.main_sequence.add_child(TopBarrier(name="drop_top",state=True))
        self.main_sequence.add_child(UpdateNoisettePos(name="RemoveForbidden",doNewForbidden=False))
        self.main_sequence.add_child(GetClosestPantry(name="get_pantry_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_pantry"))
        self.main_sequence.add_child(BottomBarrier(name="lift_bot",state=False))
        self.main_sequence.add_child(UpdateNoisettePos(name="ChangeForbidden"))
        #self.main_sequence.add_child(Move(name="go_back",value=300))

class ProcedurePushNoisetteMagicoBus(py_trees.decorators.PassThrough):
    def __init__(self, name: str,):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetClosestNoisette(name="get_Noisette_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette"))
        self.main_sequence.add_child(TopBarrier(name="lift_top",state=False))
        self.main_sequence.add_child(BottomBarrier(name="drop_bot",state=True))
        self.main_sequence.add_child(Move(name="push_noisette",value=200))
        self.main_sequence.add_child(TopBarrier(name="drop_top",state=True))
        self.main_sequence.add_child(UpdateNoisettePos(name="RemoveForbidden",doNewForbidden=False))
        self.main_sequence.add_child(GetClosestPantry(name="get_pantry_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_pantry"))
        self.main_sequence.add_child(BottomBarrier(name="lift_bot",state=False))
        self.main_sequence.add_child(UpdateNoisettePos(name="ChangeForbidden"))
        #self.main_sequence.add_child(Move(name="go_back",value=300))

class ProcedurePushNoisetteChasseNeige(py_trees.decorators.PassThrough):
    def __init__(self, name: str,):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetNextNoisette(name="get_Noisette_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette"))
        self.main_sequence.add_child(Move(name="push_noisette",value=200))
        self.main_sequence.add_child(UpdateNoisettePos(name="ChangeForbidden"))
        self.main_sequence.add_child(Move(name="go_back",value=-300))


class GetNextNoisette(GetLoc):
    def __init__(self, name: str, ):
        super().__init__(name)
        order=[2,3,1,0]
        self.queue=[robot.noisettes[i] for i in order] 
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        
    def getNextLoc(self):
        robot.update()
        res=self.queue.pop(0)
        self.blackboard.nutBox=res
        return res.getPushpos(buffer=0)

class GetClosestNoisette(GetLoc):
    def __init__(self, name: str, ):
        super().__init__(name)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        #self.noisettes=[Position(100, 700,90),Position(100, 1500,90), Position(1050, 1125,0),Position(1000, 1750,0),Position(2750, 700,90),Position(2750, 1500,90),Position(1750, 1125,0),Position(1800, 1750,0)]
        #self.queue=[noisette.getPushpos(buffer=0) for noisette in robot.noisettes]
        #self.queue=[Position(2800, 1200,0)]
        self.queue=robot.noisettes
        
    def getNextLoc(self):
        robot.update()
        #self.queue = sorted(self.queue, key=lambda nb: robot.graph.getDist(robot.pos, nb.pos))
        self.queue = sorted(self.queue, key=lambda nb: robot.pos.distance(nb.pos))
        res=self.queue.pop(0)
        self.blackboard.nutBox=res
        return res.getPushpos(buffer=0)

class GetClosestPantry(GetLoc):
    def __init__(self, name: str, ):
        super().__init__(name)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        #self.noisettes=[Position(100, 700,90),Position(100, 1500,90), Position(1050, 1125,0),Position(1000, 1750,0),Position(2750, 700,90),Position(2750, 1500,90),Position(1750, 1125,0),Position(1800, 1750,0)]
        #self.queue=[noisette.getPushpos(buffer=0) for noisette in robot.noisettes]
        #self.queue=[Position(2800, 1200,0)]
        self.queue=robot.pantries

    def getNextLoc(self):
        robot.update()
        #self.queue = sorted(self.queue, key=lambda nb: robot.graph.getDist(robot.pos, nb.pos))
        self.queue = sorted(self.queue, key=lambda nb: robot.pos.distance(nb))
        return super().getNextLoc()


class UpdateNoisettePos(py_trees.behaviour.Behaviour):
    """Updates the NutBox position after being pushed"""

    def __init__(self, name: str, doNewForbidden=True):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="UpdateNoisettePos")
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.READ)
        self.doNewForbidden=doNewForbidden
        
    def update(self):
        noisette = self.blackboard.nutBox
        #noisette.pos=robot.getNutBoxPosMagicoBus()
        noisette.setCenter(robot.getNutBoxPosChasseNeige())
        robot.graph.removeForbidden(noisette.index)
        if self.doNewForbidden:
            buffer=75
            xmin, xmax, ymin, ymax = noisette.getForbiddenZone(buffer=buffer+Robot.WIDTH // 2)
            noisette.index = robot.graph.addForbidden(xmin, xmax, ymin, ymax)
        return py_trees.common.Status.SUCCESS
    

#Créer un arbre de comportement très basique pour tester
if __name__ == "__main__":
    robot=Robot(Position(0,0,0))
    root = py_trees.composites.Sequence("MainSequence", memory=True)
    #getA = GetLoc(name="movetoA")
    #movetoA = GoToLoc(name="movetoA")
    procedure = ProcedurePushNoisetteChasseNeige(name="main")

    root.add_children([
        procedure
    ])
    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(py_trees.display.unicode_tree(root=root))
    behaviour_tree.setup(timeout=15)


    def print_tree(tree: py_trees.trees.BehaviourTree) -> None:
        """Print the behaviour tree and its current status."""
        print(py_trees.display.unicode_tree(root=tree.root, show_status=True))

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    try:
        behaviour_tree.tick_tock(
            period_ms=100,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=robot.comm.tick_simulation,
            post_tick_handler=print_tree
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()