#!/usr/bin/env python3

import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from utilities.logging_setup import setup_logging

setup_logging()

import py_trees
from behaviour_tree.utilities.robot import RobotChasseNeige, NutBox, AREA_WIDTH
from behaviour_tree.behaviours.strategieChasseNeige import ProcedureNoisette, PushCurrentNutBoxChildren, Setup, GetNextNoisette
from behaviour_tree.behaviours.basicBehaviours import Start, GetSide, CheckTime, SetLoc, GoToLoc, CheckLidar, Stop, Move, Rotate, SetPosOffset, SetStartPos
from utilities.position import Position

import argparse

parser = argparse.ArgumentParser(description="Run robot controller in Sim or Hardware mode.")
parser.add_argument(
    "--sim", 
    action="store_true", 
    help="Run in simulation mode"
)

SIMULATION = parser.parse_args().sim

if SIMULATION:
    from simulation.simulation import SimRobot
    from simulation.communicationSimulation import CommSim as Comm
else:
    from canBus.CommunicationCan import CommunicationCan as Comm

if __name__ == "__main__":
    DISTANCE_CODEUSES = 54
    START_POS = Position(420, RobotChasseNeige.DISTANCE_CODEUSES, 90)
    ORDER=[0] #for left side
    TIMEGOBACK= 80 # seconds until robot should start going back to start position
    USELIDAR = True
    USECAMERA = True
    ILDE_TIME_BUFFER = 2 # seconds minimum to wait after each action before starting the next one
    ACTION_TIMEOUT = 10 # seconds to wait before considering an action failed 
    
    logger = logging.getLogger(__name__)
    logger.info("===== Main Program Started =====")
    logger.info(f"Start position: {START_POS}, Order: {ORDER}, Go-back time limit: {TIMEGOBACK}s")
    
    if SIMULATION:
        simStartPos = START_POS.getSymmetric(AREA_WIDTH)
        simRobot = SimRobot(
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
        action_timeout=ACTION_TIMEOUT
    )
    #Position of front of robot (Not centered around codeuses) when pushing noisette, where camera is checked 
    PUSH_POSITIONS = [
        Position(275, 900, 270),   #0
        Position(275, 1700, 270),   #1
        None,   #2
        Position(1000, 1725, 0),   #3
        None,   #4
        None,   #5
        None,   #6
        None    #7
    ]

    # distance needed to push noisette from push position to fit all 4 nutboxes in the pantry
    PUSH_DISTANCES = [
        400,   #0
        400,   #1
        360,   #2
        410,   #3
        200,   #4
        200,   #5
        200,   #6
        200    #7
    ]
    
    GO_BACK_POS = Position(150, 100, 90)

    root = py_trees.composites.Sequence("MainSequence", memory=True)
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    root.add_child(SetStartPos(name="set_start_pos", robot=robot, startPos=START_POS))
    root.add_child(SetPosOffset(name="set_pos_offset", robot=robot))
    root.add_child(Setup(name="setup", order=ORDER, PUSH_POSITIONS=PUSH_POSITIONS, PUSH_DISTANCES=PUSH_DISTANCES, USECAMERA=USECAMERA, robot=robot))

    sequence_strategie = py_trees.composites.Sequence("sequence_strategie", memory=True)
    
    sequence_strategie.add_child(Move(name="Move1", value=260+RobotChasseNeige.HEIGHT-DISTANCE_CODEUSES, robot=robot))
    sequence_strategie.add_child(GetNextNoisette(name="Push", robot=robot))
    sequence_strategie.add_child(PushCurrentNutBoxChildren(name="Push", robot=robot))
    sequence_strategie.add_child(Move(name="goBack", value=-700, robot=robot))    
    root.add_child(sequence_strategie)
    
    

    robot.startBT(root, robot)