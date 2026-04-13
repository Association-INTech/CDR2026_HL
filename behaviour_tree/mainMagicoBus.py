import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from behaviour_tree.utilities.communication import CommSim
from behaviour_tree.utilities.robot import robotMagicoBus
from behaviour_tree.behaviours.strategieMagicoBus import ProcedurePushNoisette
from behaviour_tree.simulation.simulation import SimRobotMagicoBus
from behaviour_tree.utilities.position import Position

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    
    simRobot = SimRobotMagicoBus(
        pos=startPos,
        speed=250,
    )
    comm = CommSim(simRobot)
    robot = robotMagicoBus(pos=startPos, comm=comm)

    root = ProcedurePushNoisette("PushNoisette", robot)
    robot.startBT(root, robot)