import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
import os

# Setup py_trees file logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'py_trees.log')),
        logging.StreamHandler()
    ]
)

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
    robot = robotMagicoBus(pos=startPos, simRobot=simRobot)

    root = ProcedurePushNoisette("PushNoisette", robot)
    robot.startBT(root, robot)