from simulation import Simulation
from position import Position

class Comm:
    """Classe qui gère la communication avec le LL, on ajoutera les messages CAN ici"""
    #def __init__(self):
    def start_move(self,dist):
        print(f"moved {dist}")
    def start_rotate(self, angle):
        print(f"rotated {angle}")
    def get_position(self):
        return None
    def get_feedback(self,id):
        return True
    def putTopBarrier(self,state):
        print(f"Top Barrier: {state}")
    def putBottomBarrier(self,state):
        print(f"Bottom Barrier: {state}")


class CommSim(Comm):
    """Classe qui gère la communication avec le LL, simulé avec pygame"""
    def __init__(self):
        self.simulation = Simulation(0.5, auto_start=False)
    def start_move(self,dist):
        self.simulation.robot.start_move(dist)
    def start_rotate(self, angle):
        self.simulation.robot.rotate(angle)
    def get_position(self):
        x,y=self.simulation.robot.getCenterPos()
        angle=self.simulation.robot.angle%360
        return Position(x,y,angle)
    def get_feedback(self,id):
        #print(f"Feedback {id}:{self.simulation.robot.move_remaining}")
        return (self.simulation.robot.move_remaining == 0)
    def putTopBarrier(self,state):
        self.simulation.robot.isTopDown=state
    def putBottomBarrier(self,state):
        self.simulation.robot.isBottomDown=state
