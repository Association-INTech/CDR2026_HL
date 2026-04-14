#!/usr/bin/env python3

import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from behaviour_tree.utilities.logging_setup import setup_logging

setup_logging()

import py_trees
from behaviour_tree.utilities.robot import RobotChasseNeige
from behaviour_tree.behaviours.strategieChasseNeige import ProcedureNoisette, setup
from behaviour_tree.behaviours.basicBehaviours import Start, GetSide, CheckTime, SetLoc, GoToLoc, CheckLidar, Stop, Move, Rotate
from behaviour_tree.utilities.position import Position

import argparse

parser = argparse.ArgumentParser(description="Run robot controller in Sim or Hardware mode.")
parser.add_argument(
    "--sim", 
    action="store_true", 
    help="Run in simulation mode"
)

SIMULATION = parser.parse_args().sim

if SIMULATION:
    from behaviour_tree.simulation.simulation import SimRobot
    from behaviour_tree.utilities.communicationSimulation import CommSim as Comm
else:
    from canBus.CommunicationCan import CommunicationCan as Comm

if __name__ == "__main__":
    DISTANCE_CODEUSES = 54
    startPos = Position(270, DISTANCE_CODEUSES, 90)
    ORDER=[2,3,0] #for left side
    TIMEGOBACK= 80 # seconds until robot should start going back to start position
    USELIDAR = False
    USECAMERA = True
    
    logger = logging.getLogger(__name__)
    logger.info("===== Main Program Started =====")
    logger.info(f"Start position: {startPos}, Order: {ORDER}, Go-back time limit: {TIMEGOBACK}s")
    
    if SIMULATION:
        simRobot = SimRobot(
        pos=startPos,
        speed=250,
        )
        comm = Comm(simRobot,startPos=startPos)
    else:
        comm = Comm(startPos=startPos)
    
    robot = RobotChasseNeige(pos=startPos, comm=comm)

    root = py_trees.composites.Sequence("MainSequence", memory=True)
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    
    root.add_child(setup(name="setup", order=ORDER, robot=robot))
    
    sequence_strategie = py_trees.composites.Sequence("sequence_strategie", memory=True)
    
    sequence_strategie.add_child(Move(name="Move1", value=500, robot=robot))
    sequence_strategie.add_child(Rotate(name="Rotate1", value=180, robot=robot))
    sequence_strategie.add_child(Move(name="Move2", value=500, robot=robot))    
    root.add_child(sequence_strategie)
    
    

    robot.startBT(root, robot)