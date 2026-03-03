import random
import py_trees
import time

from position import Position
#from communication import Comm
from communication import CommSim as Comm

from graph import GridGraph

AREA_WIDTH = 3000
AREA_HEIGHT = 3000


class Robot:
    "Gère toutes les actions tout relatif au robot"
    WIDTH=376
    HEIGHT=200

    
    def __init__(self, pos):
        self.pos=pos
        self.comm=Comm()
        self.actions=[]
        self.__countID=0 #variable de classe pour avoir un id
        self.start_time = time.time()
        self.logger = py_trees.logging.Logger("Robot")
        self.graph=GridGraph(AREA_WIDTH,AREA_HEIGHT,scale=10)
        #self.graph.addForbidden(800,1500,0,1500)
        
        self.noisettes = [
            NutBox(Position(100, 700, 90)),
            NutBox(Position(100, 1500, 90)),
            NutBox(Position(1050, 1125, 0)),
            NutBox(Position(1000, 1750, 0)),
            NutBox(Position(2750, 700, 90)),
            NutBox(Position(2750, 1500, 90)),
            NutBox(Position(1750, 1125, 0)),
            NutBox(Position(1800, 1750, 0))
        ]        
        self.nutBoxGroupForbidden()
            
    
    def nutBoxGroupForbidden(self):
        for noisette in self.noisettes:
            xmin,xmax,ymin,ymax=noisette.getForbiddenZone(buffer=Robot.WIDTH//2)
            noisette.index=self.graph.addForbidden(xmin,xmax,ymin,ymax)

    def getNutBoxPos(self):
        return self.pos.foward(Robot.HEIGHT//2) #en mode chasse neige

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

    def is_moving(self):
        self.update()
        return len(self.actions)!=0 #check if actions empty

class NutBox():
    WIDTH=150
    HEIGHT=50
    
    def __init__(self,pos):
        self.pos=pos #top right pos
        self.index=None
        
    def getPushpos(self,buffer=0):
            if self.pos.angle==0:
                return self.pos.add(Position(-buffer,NutBox.WIDTH//2,0))
            else:
                return self.pos.add(Position(NutBox.WIDTH//2,buffer,0))
            
    def getForbiddenZone(self,buffer):
        if self.pos.angle==0:
            sizex=200
            sizey=150
        else:
            sizex=150
            sizey=200
        return (self.pos.x-buffer,self.pos.x+sizex+buffer,self.pos.y-buffer,self.pos.y+sizey+buffer)
        

class GetLoc(py_trees.behaviour.Behaviour):
    """Obtient le prochain endroit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="GetLoc")
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.WRITE)
        self.queue = [
            Position(
                random.randint(0, 3000),
                random.randint(1, 2000),
                random.uniform(0, 360)
            )
            for _ in range(3)
        ]
        self.queue.append(Position(0,0,0))


    def update(self):
        if len(self.queue)==0:
            return py_trees.common.Status.FAILURE
        self.blackboard.loc=self.queue.pop(0)
        self.logger.debug(f"Going to {str(self.blackboard.loc)}")
        return py_trees.common.Status.SUCCESS


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
            if (diff.x==0 and diff.angle==0):
                return (Move,abs(diff.y))
            if (diff.x==0 and diff.y==0):
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

class ProcedurePushNoisette(py_trees.decorators.PassThrough):
    def __init__(self, name: str,):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetNoisette(name="get_Noisette_location"))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette"))
        self.main_sequence.add_child(Move(name="push_noisette",value=200))
        self.main_sequence.add_child(Move(name="go_back",value=-200))
    
    def terminate(self, new_status):
        
        return super().terminate(new_status)



class GetNoisette(GetLoc):
    def __init__(self, name: str, ):
        super().__init__(name)
        #self.noisettes=[Position(100, 700,90),Position(100, 1500,90), Position(1050, 1125,0),Position(1000, 1750,0),Position(2750, 700,90),Position(2750, 1500,90),Position(1750, 1125,0),Position(1800, 1750,0)]
        self.queue=[noisette.getPushpos(buffer=0) for noisette in robot.noisettes]
        #self.queue=[Position(2800, 1200,0)]

class UpdateNoisettePos(py_trees.behaviour.Behaviour):
    """Updates the NutBox position after being pushed"""

    def __init__(self, name: str):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="UpdateNoisettePos")
        self.blackboard.register_key(key="noisette_index", access=py_trees.common.Access.READ)

    def update(self):
        index = self.blackboard.noisette_index
        noisette = robot.noisettes[index]
        noisette.pos=robot.getNutBoxPos()
        robot.graph.removeForbidden(noisette.index)
        xmin, xmax, ymin, ymax = noisette.getForbiddenZone(buffer=Robot.WIDTH // 2)
        noisette.index = robot.graph.addForbidden(xmin, xmax, ymin, ymax)
        return py_trees.common.Status.SUCCESS
    

#Créer un arbre de comportement très basique pour tester
if __name__ == "__main__":
    robot=Robot(Position(0,0,0))
    root = py_trees.composites.Sequence("MainSequence", memory=True)
    #getA = GetLoc(name="movetoA")
    #movetoA = GoToLoc(name="movetoA")
    procedure = ProcedurePushNoisette(name="main")

    root.add_children([
        procedure
    ])
    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(py_trees.display.unicode_tree(root=root))
    behaviour_tree.setup(timeout=15)

    
    
    def tick_simulation(tree: py_trees.trees.BehaviourTree) -> None:
        """Update simulation before each behavior tree tick."""

        if not robot.comm.simulation.tick():
            # Simulation was closed, interrupt the behavior tree
            tree.interrupt()


    def print_tree(tree: py_trees.trees.BehaviourTree) -> None:
        """Print the behaviour tree and its current status."""
        print(py_trees.display.unicode_tree(root=tree.root, show_status=True))

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    try:
        behaviour_tree.tick_tock(
            period_ms=100,
            number_of_iterations=py_trees.trees.CONTINUOUS_TICK_TOCK,
            pre_tick_handler=tick_simulation,
            post_tick_handler=print_tree
        )
    except KeyboardInterrupt:
        behaviour_tree.interrupt()