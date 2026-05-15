#!/usr/bin/env python3

from ast import Or
from math import dist
import sys
from pathlib import Path

# Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from utilities.logging_setup import setup_logging

setup_logging()

import py_trees
from behaviour_tree.utilities.robot import RobotChasseNeige, AREA_WIDTH
from utilities.position import Position
from behaviour_tree.behaviours.strategieChasseNeige import (
    PushCurrentNutBoxChildren,
    Setup,
    GetNextNoisette,
    ProcedureHardCoded,
)
from behaviour_tree.strat_hardcoded.strat_2_3_0 import Strat230
from behaviour_tree.strat_hardcoded.strat_0_2_5_3_4 import Strat02534
from behaviour_tree.strat_hardcoded.strat_2_3_1_0 import Strat2310

from behaviour_tree.behaviours.basicBehaviours import (
    CheckLidar,
    Rotate,
    Start,
    GetSide,
    Move,
    SetPosOffset,
    SetStartPos,
    Stop,
)
import argparse


GAUCHE = 270
DROITE = 360 - GAUCHE

parser = argparse.ArgumentParser(
    description="Run robot controller in Sim or Hardware mode."
)
parser.add_argument("--sim", action="store_true", help="Run in simulation mode")
parser.add_argument("--nb0", type=int, default=4, help="box count to push for pantry 0")
parser.add_argument(
    "--nb1", type=int, default=4, help="box count to push for pantry 1."
)
parser.add_argument(
    "--nb2", type=int, default=4, help="box count to push for pantry 2."
)
parser.add_argument(
    "--nb3", type=int, default=4, help="box count to push for pantry 3."
)
parser.add_argument(
    "--nb4", type=int, default=4, help="box count to push for pantry 4."
)
parser.add_argument(
    "--nb5", type=int, default=4, help="box count to push for pantry 5."
)
parser.add_argument(
    "--nb6", type=int, default=4, help="box count to push for pantry 6."
)
parser.add_argument(
    "--nb7", type=int, default=4, help="box count to push for pantry 7."
)
parser.add_argument(
    "--strat",
    choices=["230", "2310", "02534"],
    default="230",
    help="Choose the hard-coded strategy to run.",
)

args = parser.parse_args()
SIMULATION = args.sim
strategy = args.strat

strategies = {
    "230": Strat230,
    "2310": Strat2310,
    "02534": Strat02534,
}
current_strategy = strategies[strategy]
pose_depart = current_strategy.get_start_pos(RobotChasseNeige)

NB_0 = args.nb0
NB_1 = args.nb1
NB_2 = args.nb2
NB_3 = args.nb3
NB_4 = args.nb4
NB_5 = args.nb5
NB_6 = args.nb6
NB_7 = args.nb7

nb_list = [NB_0, NB_1, NB_2, NB_3, NB_4, NB_5, NB_6, NB_7]

if SIMULATION:
    from simulation.simulation import SimRobotChasseNeige
    from simulation.communicationSimulation import CommSim as Comm
else:
    from canBus.CommunicationCan import CommunicationCan as Comm

if __name__ == "__main__":
    DISTANCE_CODEUSES = 54
    START_POS = current_strategy.get_start_pos(RobotChasseNeige)
    ORDER = [0]  # for left side
    TIMEGOBACK = 80  # seconds until robot should start going back to start position
    USELIDAR = True
    USECAMERA = False
    ILDE_TIME_BUFFER = 2 # seconds minimum to wait after each action before starting the next one
    END_TIME_BUFFER = 2 # seconds minimum to wait after finishing an action before considering the next one
    ACTION_TIMEOUT = 1000000  # seconds to wait before considering an action failed

    logger = logging.getLogger(__name__)
    logger.info("===== Main Program Started =====")
    logger.info(
        f"Start position: {START_POS}, Order: {ORDER}, Go-back time limit: {TIMEGOBACK}s"
    )
    logger.info(f"Strategy: {strategy}, NB counts: {nb_list}")

    if SIMULATION:
        simStartPos = START_POS.getSymmetric(AREA_WIDTH)
        simRobot = SimRobotChasseNeige(
            pos=START_POS,
            speed=250,
        )
        comm = Comm(simRobot)
    else:
        comm = Comm()

    robot = RobotChasseNeige(
        pos=START_POS,
        comm=comm,
        idle_time_buffer=ILDE_TIME_BUFFER,
        end_time_buffer=END_TIME_BUFFER,
        action_timeout=ACTION_TIMEOUT,
        USE_GRAPH=False,
        USELIDAR=USELIDAR,
    )
    # Position of front of robot (Not centered around codeuses) when pushing noisette, where camera is checked
    PUSH_POSITIONS = [
        Position(275, 900, 270),  # 0
        Position(275, 1700, 270),  # 1
        None,  # 2
        Position(1000, 1725, 0),  # 3
        None,  # 4
        None,  # 5
        None,  # 6
        None,  # 7
    ]

    # distance needed to push noisette from push position to fit all 4 nutboxes in the pantry
    PUSH_DISTANCES = [
        400,  # 0
        400,  # 1
        360,  # 2
        410,  # 3
        200,  # 4
        200,  # 5
        200,  # 6
        200,  # 7
    ]

    GO_BACK_POS = Position(150, 100, 90)

    # Create the behavior tree
    root = py_trees.composites.Sequence("MainSequence", memory=True)

    # --- Startup  ---
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    root.add_child(SetStartPos(name="set_start_pos", robot=robot, startPos=START_POS))
    root.add_child(SetPosOffset(name="set_pos_offset", robot=robot))
    root.add_child(
        Setup(
            name="setup",
            order=ORDER,
            PUSH_POSITIONS=PUSH_POSITIONS,
            PUSH_DISTANCES=PUSH_DISTANCES,
            USECAMERA=USECAMERA,
            robot=robot,
        )
    )

    # --- Main Strategy ---
    sequence_strategie = py_trees.composites.Sequence(
        "sequence_strategie", memory=False
    )

    sequence_main = py_trees.composites.Sequence("sequence_main", memory=True)

    # ------------------------------------------------------------------------------------------------------------------------

    strat = current_strategy.get_strat(GAUCHE, DROITE, nb_list)

    sequence_main.add_child(
        ProcedureHardCoded(name="ProcedureHardCoded", strategy=strat, robot=robot)
    )

    sequence_strategie.add_child(sequence_main)

    root.add_child(sequence_strategie)

    # --- Start the behavior tree ---
    robot.startBT(root, robot)
