import py_trees
import time
from position import Position
from robot import Robot
from basicBehaviours import GetLoc, GoToLoc, Move, TopBarrier, BottomBarrier, UpdateNoisettePos

class ProcedurePushNoisetteChasseNeige(py_trees.decorators.PassThrough):
    def __init__(self, name: str, robot):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetNextNoisette(name="get_Noisette_location", robot=robot))
        self.main_sequence.add_child(GoToLoc(name="go_to_noisette", robot=robot))
        self.main_sequence.add_child(Move(name="push_noisette", robot=robot, value=200))
        self.main_sequence.add_child(UpdateNoisettePos(name="ChangeForbidden", robot=robot))
        self.main_sequence.add_child(Move(name="go_back", robot=robot, value=-300))


class GetNextNoisette(GetLoc):
    def __init__(self, name: str, robot):
        super().__init__(name, robot)
        order=[2,3,1,0]
        self.queue=[self.robot.noisettes[i] for i in order] 
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        
    def getNextLoc(self):
        self.robot.update()
        res=self.queue.pop(0)
        self.blackboard.nutBox=res
        return res.getPushpos(buffer=0)



