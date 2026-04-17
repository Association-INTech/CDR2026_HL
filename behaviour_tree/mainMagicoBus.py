import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from utilities.logging_setup import setup_logging

setup_logging()

from behaviour_tree.utilities.robot import RobotMagicoBus
from behaviour_tree.behaviours.strategieMagicoBus import ProcedurePushNoisette
from simulation.simulation import SimRobotMagicoBus
from utilities.position import Position
from simulation.communicationSimulation import CommSim

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    
    simRobot = SimRobotMagicoBus(
        pos=startPos,
        speed=250,
    )
    comm = CommSim(simRobot)
    robot = RobotMagicoBus(pos=startPos, comm=comm)

    root = ProcedurePushNoisette("PushNoisette", robot)
    robot.startBT(root, robot)