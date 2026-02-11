import random
import py_trees
import time

from position import Position
#from communication import Comm
from communication import CommSim as Comm

class Robot:
    "Gère toutes les actions tout relatif au robot"
    def __init__(self, pos):
        self.pos=pos
        self.comm=Comm()
        self.actions=[]
        self.__countID=0 #variable de classe pour avoir un id
        self.start_time = time.time()
    

    def getID(self):
        self.__countID+=1
        return self.__countID

    def getPos(self):
        self.update()
        return self.pos
    
    def update(self):
        self.pos=self.comm.get_position()
        for id in self.actions:
            if self.comm.get_feedback(id):
                self.actions.remove(id)

    def start_move(self,dist):
        id=self.getID()
        self.comm.start_move(dist)
        self.actions.append(id)
        return id

    def start_rotate(self, angle):
        id=self.getID()
        self.comm.start_rotate(angle)
        self.actions.append(id)
        return id

    def is_moving(self):
        self.update()
        return len(self.actions)!=0 #check if actions empty



class GetLoc(py_trees.behaviour.Behaviour):
    """Obtient le prochain endroit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="GetLoc")
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.WRITE)

    def setup(self):
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
        return py_trees.common.Status.SUCCESS


class GoToLoc(py_trees.decorators.PassThrough):
    """Va à l'endroit choisi"""

    def __init__(self, name: str):
        self.main_sequence = py_trees.composites.Sequence("MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.blackboard = self.attach_blackboard_client(name="GoToLoc")
        self.blackboard.register_key(key="loc", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="plan", access=py_trees.common.Access.WRITE)

    def initialise(self):
        self.main_sequence.remove_all_children()
        self.createPlan()
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


#Créer un arbre de comportement très basique pour tester
if __name__ == "__main__":
    robot=Robot(Position(0,0,0))
    root = py_trees.composites.Sequence("MainSequence", memory=True)
    getA = GetLoc(name="movetoA")
    movetoA = GoToLoc(name="movetoA")

    root.add_children([
        GetLoc("GetA"),
        GoToLoc("GoA"),
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