import py_trees
import time
from position import Position
from robot import Robot

class GetLoc(py_trees.behaviour.Behaviour):
    """Obtient le prochain endroit"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot
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

    def __init__(self, name: str, robot):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.robot = robot
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

        currentPos = self.robot.getPos()
        dx = self.blackboard.loc.x - currentPos.x
        dy = self.blackboard.loc.y - currentPos.y

        def addStep(step_class, value):
            steps.append((step_class.__name__, value))
            stepsBT.append(step_class(
                name=f"{step_class.__name__}_{value}",
                robot=self.robot,
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

        currentPos = self.robot.getPos()
        targetPos = Position(self.blackboard.loc.x,self.blackboard.loc.y,self.blackboard.loc.angle)

        def addStep(step_class, value):
            steps.append((step_class.__name__, value))
            stepsBT.append(step_class(
                name=f"{step_class.__name__}_{value}",
                robot=self.robot,
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

        path=self.robot.graph.getShortestPathPos(currentPos,targetPos)

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

    def __init__(self, name: str, robot, value: float) -> None:
        super().__init__(name)
        self.robot = robot
        self.angle = value

    def initialise(self):
        self.start_time=time.time()
        self.id=self.robot.start_rotate(self.angle)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if self.robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS        
               
class Move(py_trees.behaviour.Behaviour):
    """Move robot forward by a given distance"""

    def __init__(self, name: str, robot, value: float) -> None:
        super().__init__(name)
        self.robot = robot
        self.distance = value

    def initialise(self):
        self.start_time=time.time()
        self.id=self.robot.start_move(self.distance)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if self.robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class TopBarrier(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, robot, state: bool) -> None:
        super().__init__(name)
        self.robot = robot
        self.state = state

    def initialise(self):
        self.start_time=time.time()
        self.id=self.robot.top_barrier(self.state)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if self.robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class BottomBarrier(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, robot, state: bool) -> None:
        super().__init__(name)
        self.robot = robot
        self.state = state

    def initialise(self):
        self.start_time=time.time()
        self.id=self.robot.bottom_barrier(self.state)

    def update(self):
        if time.time() - self.start_time > 10:
            return py_trees.common.Status.FAILURE
        if self.robot.is_moving():
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS

class UpdateNoisettePos(py_trees.behaviour.Behaviour):
    """Updates the NutBox position after being pushed"""

    def __init__(self, name: str, robot, doNewForbidden=True):
        super().__init__(name)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name="UpdateNoisettePos")
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.READ)
        self.doNewForbidden=doNewForbidden
        
    def update(self):
        noisette = self.blackboard.nutBox
        noisette.setCenter(self.robot.getNutBoxPos())
        self.robot.graph.removeForbidden(noisette.index)
        if self.doNewForbidden:
            buffer=75
            xmin, xmax, ymin, ymax = noisette.getForbiddenZone(buffer=buffer+Robot.WIDTH // 2)
            noisette.index = self.robot.graph.addForbidden(xmin, xmax, ymin, ymax)
        return py_trees.common.Status.SUCCESS
    
