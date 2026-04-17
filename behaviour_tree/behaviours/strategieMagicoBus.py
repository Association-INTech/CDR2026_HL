import py_trees
from utilities.position import Position
from behaviour_tree.utilities.robot import Robot
from behaviour_tree.behaviours.basicBehaviours import GetLoc, Move, UpdateNoisettePos, TopBarrier, BottomBarrier, GoToLoc

class ProcedurePushNoisette(py_trees.decorators.PassThrough):
    def __init__(self, name: str, robot):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetClosestNoisette(name="get_Noisette_location", robot=robot))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette", robot=robot))
        self.main_sequence.add_child(TopBarrier(name="lift_top", robot=robot, state=False))
        self.main_sequence.add_child(BottomBarrier(name="drop_bot", robot=robot, state=True))
        self.main_sequence.add_child(Move(name="push_noisette", robot=robot, value=200))
        self.main_sequence.add_child(TopBarrier(name="drop_top", robot=robot, state=True))
        self.main_sequence.add_child(UpdateNoisettePos(name="RemoveForbidden", robot=robot, doNewForbidden=False))
        self.main_sequence.add_child(GetClosestPantry(name="get_pantry_location", robot=robot))
        self.main_sequence.add_child(GoToLoc(name="go_to_pantry", robot=robot))
        self.main_sequence.add_child(BottomBarrier(name="lift_bot", robot=robot, state=False))
        self.main_sequence.add_child(UpdateNoisettePos(name="ChangeForbidden", robot=robot))
        #self.main_sequence.add_child(Move(name="go_back", robot=robot, value=300))

class GetClosestNoisette(GetLoc):
    def __init__(self, name: str, robot):
        super().__init__(name, robot)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        self.queue=self.robot.noisettes
        
    def getNextLoc(self):
        self.robot.update()
        self.queue = sorted(self.queue, key=lambda nb: self.robot.pos.distance(nb.pos))
        res=self.queue.pop(0)
        self.blackboard.nutBox=res
        return res.getPushpos(buffer=0)

class GetClosestPantry(GetLoc):
    def __init__(self, name: str, robot):
        super().__init__(name, robot)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        self.queue=self.robot.pantries

    def getNextLoc(self):
        self.robot.update()
        self.queue = sorted(self.queue, key=lambda nb: self.robot.pos.distance(nb))
        return super().getNextLoc()
