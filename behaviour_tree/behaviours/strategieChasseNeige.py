import py_trees
import time
import logging
from utilities.position import Position
from behaviour_tree.utilities.robot import AREA_WIDTH, Robot, NutBox
from behaviour_tree.behaviours.basicBehaviours import GetLoc, GoToLoc, Move, TopBarrier, BottomBarrier, UpdateNoisettePos, GetSide, Start, NutBoxShiftCamera, Push

logger = logging.getLogger(__name__)

class Setup(py_trees.behaviour.Behaviour):
    """setup strategy for the robot"""
    def __init__(self, name: str, order: list, PUSH_POSITIONS: list, PUSH_DISTANCES: list, USECAMERA: bool, robot):
        super().__init__(name)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="nutBoxOrder", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="side", access=py_trees.common.Access.WRITE)
        self.order=order
        self.PUSH_DISTANCES=PUSH_DISTANCES
        self.PUSH_POSITIONS=PUSH_POSITIONS
        self.USECAMERA=USECAMERA

    def update(self):
                
        if self.blackboard.side: # left
            self.blackboard.nutBoxOrder=self.order
            for i in range(len(self.robot.noisettes)):
                if self.PUSH_POSITIONS[i] is not None:
                    self.robot.noisettes[i].push_pos=self.PUSH_POSITIONS[i].forward(self.robot.HEIGHT-self.robot.DISTANCE_CODEUSES)
                if self.USECAMERA:  
                    self.robot.noisettes[i].children = [ProcedurePushNoisette(name=f"push_noisette_{i}", pushDistance=self.PUSH_DISTANCES[i], robot=self.robot)]
                else:
                    self.robot.noisettes[i].children = [Move(name=f"push_noisette_{i}", value=self.PUSH_DISTANCES[i], robot=self.robot)]

        else: #right
            self.blackboard.nutBoxOrder=[7-i for i in self.order]
            for i in range(len(self.robot.noisettes)):
                if self.PUSH_POSITIONS[7-i] is not None:
                    self.robot.noisettes[i].push_pos=self.PUSH_POSITIONS[7-i].forward(self.robot.HEIGHT-self.robot.DISTANCE_CODEUSES).getSymmetric(AREA_WIDTH)
                if self.USECAMERA:
                    self.robot.noisettes[i].children = [ProcedurePushNoisette(name=f"push_noisette_{i}", pushDistance=self.PUSH_DISTANCES[7-i], robot=self.robot)]
                else:
                    self.robot.noisettes[i].children = [Move(name=f"push_noisette_{i}", value=self.PUSH_DISTANCES[7-i], robot=self.robot)]

        
        return py_trees.common.Status.SUCCESS

class ProcedurePushNoisette(py_trees.decorators.PassThrough):
    def __init__(self, name: str, pushDistance: int, robot):
        self.main_selector = py_trees.composites.Selector(name+"MainSelector", True)
        super().__init__(name,self.main_selector)
        
        self.pushSequence = py_trees.composites.Sequence(name+"PushSequence", True)
        self.pushSequence.add_child(NutBoxShiftCamera(name=name+"_shift_camera", robot=robot))
        self.pushSequence.add_child(Push(name=name+"_shifted_push", robot=robot, pushDistance=pushDistance))
        
        self.main_selector.add_child(self.pushSequence)
        self.main_selector.add_child(Move(name=name+"_move_push", value=pushDistance, robot=robot))


class PushCurrentNutBoxChildren(py_trees.decorators.PassThrough):
    def __init__(self, name: str, robot):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name, self.main_sequence)
        self.robot = robot
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.READ)

    def initialise(self):
        self.main_sequence.remove_all_children()
        nut_box = self.blackboard.nutBox
        if nut_box is None or len(nut_box.children) == 0:
            logger.error("No nut box or no children to push")
            return
        self.main_sequence.add_children(nut_box.children)

class ProcedureNoisette(py_trees.decorators.PassThrough):
    def __init__(self, name: str, robot):
        self.main_sequence = py_trees.composites.Sequence(name+"MainSequence", True)
        super().__init__(name,self.main_sequence)
        self.main_sequence.add_child(GetNextNoisette(name=name+"get_next_noisette", robot=robot))
        self.main_sequence.add_child(GoToLoc(name=name+"go_to_noisette", robot=robot))
        self.main_sequence.add_child(PushCurrentNutBoxChildren(name=name+"push_noisette_children", robot=robot))
        self.main_sequence.add_child(UpdateNoisettePos(name=name+"update_noisette_pos", robot=robot))
        self.main_sequence.add_child(Move(name=name+"go_back", value=-200, robot=robot))



class GetNextNoisette(GetLoc):
    def __init__(self, name: str, robot):
        super().__init__(name, robot)
        self.blackboard.register_key(key="nutBox", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="nutBoxOrder", access=py_trees.common.Access.READ)
        self.queue = []
    
    def initialise(self):
        if len(self.queue) == 0:
            self.queue = [self.robot.noisettes[i] for i in self.blackboard.nutBoxOrder]
    
        
    def getNextLoc(self):
        self.robot.update()
        if len(self.queue) == 0:
            return None
        res=self.queue.pop(0)
        self.blackboard.nutBox=res
        return res.getPushpos(buffer=self.robot.HEIGHT//2)

