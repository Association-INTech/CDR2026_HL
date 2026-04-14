import py_trees
import time
from behaviour_tree.utilities.position import Position
from behaviour_tree.utilities.robot import NutBox, Robot

class GetLoc(py_trees.behaviour.Behaviour):
    """Obtient le prochain endroit"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.WRITE)
        self.queue = []
        self.queue.append(Position(0,0,0))

    def update(self):
        if len(self.queue)==0:
            self.logger.error("No more loc in queue")
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
        self.blackboard = self.attach_blackboard_client(name=name)
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
        if not self.robot.wait_for_is_idle:
            if time.time() - self.start_time > 5:
                self.logger.debug(f"Rotate action timeout: {self.angle}° in {time.time() - self.start_time:.2f}s")
                return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.RUNNING
        if time.time() - self.start_time > 5:
            self.logger.debug(f"Rotate action timeout: {self.angle}° in {time.time() - self.start_time:.2f}s")
            return py_trees.common.Status.FAILURE
        if not self.robot.is_idle():
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
        if not self.robot.wait_for_is_idle:
            if time.time() - self.start_time > 5:
                self.logger.debug(f"Move action timeout: {self.distance}mm in {time.time() - self.start_time:.2f}s")
                return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.RUNNING
        if time.time() - self.start_time > 5:
            self.logger.debug(f"Move action timeout: {self.distance}mm in {time.time() - self.start_time:.2f}s")
            return py_trees.common.Status.FAILURE
        if not self.robot.is_idle() and time.time() - self.start_time > 0.5:
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
        if not self.robot.wait_for_is_idle:
            if time.time() - self.start_time > 5:
                self.logger.debug(f"Top Barrier action timeout: {self.state} in {time.time() - self.start_time:.2f}s")
                return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.RUNNING
        if time.time() - self.start_time > 5:
            self.logger.debug(f"Top Barrier action timeout: {self.state} in {time.time() - self.start_time:.2f}s")
            return py_trees.common.Status.FAILURE
        if not self.robot.is_idle() and time.time() - self.start_time > 0.5:
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
        if not self.robot.wait_for_is_idle:
            if time.time() - self.start_time > 5:
                self.logger.debug(f"Bottom Barrier action timeout: {self.state} in {time.time() - self.start_time:.2f}s")
                return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.RUNNING
        if time.time() - self.start_time > 5:
            self.logger.debug(f"Bottom Barrier action timeout: {self.state} in {time.time() - self.start_time:.2f}s")
            return py_trees.common.Status.FAILURE
        if not self.robot.is_idle():
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
    
class Start(py_trees.behaviour.Behaviour):
    """Waits for TIRETTE signal to start"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot

    def update(self):
        tirette = True #TODO replace with actual signal
        if tirette:
            self.robot.start_time = time.time()
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.RUNNING
    
class GetSide(py_trees.behaviour.Behaviour):
    """Determine the side of the robot based on its initial position"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name="GetSide")
        self.blackboard.register_key(key="side", access=py_trees.common.Access.WRITE)

    def update(self):
        pos = self.robot.getPos()
        #TODO Replace with switch on the robot
        #TODO setup coordinates with LL
        self.blackboard.side = (pos.x < 1500)  # True: left/False: right
        return py_trees.common.Status.SUCCESS


class CheckTime(py_trees.behaviour.Behaviour):
    """Succeeds while elapsed match time is under a limit."""

    def __init__(self, name: str, robot, end_time: float):
        super().__init__(name)
        self.robot = robot
        self.end_time = end_time

    def update(self):
        elapsed = time.time() - self.robot.start_time
        self.logger.debug(f"Time: {elapsed:.2f}s elapsed")
        if elapsed < self.end_time:
            return py_trees.common.Status.SUCCESS
        self.logger.debug(f"Time limit reached: {elapsed:.2f}s elapsed, limit was {self.end_time}s")
        return py_trees.common.Status.FAILURE


class SetLoc(py_trees.behaviour.Behaviour):
    """Writes a target location on the blackboard."""

    def __init__(self, name: str, robot, loc: Position):
        super().__init__(name)
        self.robot = robot
        self.loc = loc
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.WRITE)

    def update(self):
        self.blackboard.loc = self.loc
        return py_trees.common.Status.SUCCESS
    
class NutBoxShiftCamera(py_trees.behaviour.Behaviour):
    """Writes shift from camera on the blackboard."""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="side", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="nutBoxShift", access=py_trees.common.Access.WRITE)

    def initialise(self):
        self.start_time=time.time()
    
    def update(self):
        gates = self.robot.comm.checkCamera(self.blackboard.side)
        
        if sum(gates) != 2:
            return py_trees.common.Status.RUNNING
        
        timeout = 2.0
        
        if time.time() - self.start_time > timeout:
            return py_trees.common.Status.FAILURE
        
        match gates:
            case [1, 1, 0, 0]:
                shift = -2  # décale de 2 blocs à gauche
            case [1, 0, 0, 0] | [1, 0, 1, 0] | [1, 0, 0, 1]:
                shift = -1  # décale de 1 blocs à gauche
            case [0, 0, 1, 1]:
                shift = 2   # décale de 2 blocs à droite
            case [0, 0, 0, 1] | [0, 1, 0, 1]:
                shift = 1   # décale de 1 blocs à droite
            case _:
                shift = 0   # reste sur place
                
        self.blackboard.nutBoxShift = shift
        return py_trees.common.Status.SUCCESS
        
class Push(py_trees.decorators.PassThrough):
    """Pushes the current NutBox"""

    def __init__(self, name: str, robot, pushDistance: int):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="nutBoxShift", access=py_trees.common.Access.READ)
        self.pushDistance = pushDistance

    def initialise(self):
        pushDistance = self.pushDistance + self.blackboard.nutBoxShift * NutBox.HEIGHT  # Adjust push distance
        self.main_sequence.remove_all_children()
        self.main_sequence.add_child(Move(name="PushMove", robot=self.robot, value=pushDistance))

class CheckLidar(py_trees.behaviour.Behaviour):
    """Checks the lidar for obstacles"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot
    def update(self):
        pos = self.robot.getPos()
        is_obstacle = self.robot.comm.lidar(pos)
        if is_obstacle:
            self.logger.info("Lidar: Obstacle detected")
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS
    
class Stop(py_trees.behaviour.Behaviour):
    """Stop robot"""

    def __init__(self, name: str, robot):
        super().__init__(name)
        self.robot = robot

    def initialise(self):
        self.id=self.robot.stop()
        
    def update(self):
        if self.robot.comm.get_feedback(self.id):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE