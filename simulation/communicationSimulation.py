import logging

from utilities.position import Position
from simulation.simulation import Simulation
from utilities.communication import Comm


logger = logging.getLogger(__name__)

class CommSim(Comm):
    """Classe qui gère la communication avec le LL, simulé avec pygame"""
    def __init__(self,simRobot):
        super().__init__()
        self.simulation = Simulation(0.5, auto_start=False,robot=simRobot)
        
    def start_move(self,dist):
        self.simulation.robot.start_move(dist)
    def start_rotate(self, angle):
        self.simulation.robot.rotate(angle)
    def stop(self):
        self.simulation.robot.move_remaining=0
    def get_position(self):
        return self.simulation.robot.getCenterPos()
    def get_feedback(self,id=None):
        logger.debug("Feedback %s: %s", id, self.simulation.robot.move_remaining)
        return (self.simulation.robot.move_remaining == 0)
    def putTopBarrier(self,state):
        self.simulation.robot.isTopDown=state
    def putBottomBarrier(self,state):
        self.simulation.robot.isBottomDown=state
    def tick_simulation(self, tree):
        """Update simulation before each behavior tree tick."""
        if not self.simulation.tick():
            # Simulation was closed, interrupt the behavior tree
            tree.interrupt()
    def link_frobidden(self, forbidden_zones):
        self.simulation.forbidden_zones = forbidden_zones  # same reference
        
    def getSide(self):
        """Determine the side based on pos"""
        if self.simulation.robot.getCenterPos().x < self.simulation.width / 2:
            return True  # Left (yellow)
        else:
            return False  # Right (blue)


    def checkCamera(self, side):
        """Simulate the camera gates from the robot position and the nut box colors."""
        robot_pos = self.simulation.robot.getCenterPos()
        target_color = self.simulation.yellow if side else self.simulation.blue

        nut_box_group = min(self.simulation.nutBoxGroups, key=lambda group: robot_pos.distance(group.pos))
        ordered_boxes = sorted(
            nut_box_group.nutBoxes,
            key=lambda box: (box.pos.y, box.pos.x) if nut_box_group.pos.angle % 180 == 0 else (box.pos.x, box.pos.y),
        )
        return [0 if box.color == target_color else 1 for box in ordered_boxes]
