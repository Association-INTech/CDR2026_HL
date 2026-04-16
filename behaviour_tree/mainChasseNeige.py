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
from behaviour_tree.utilities.robot import RobotChasseNeige, AREA_WIDTH
from behaviour_tree.behaviours.strategieChasseNeige import ProcedureNoisette, setup
from behaviour_tree.behaviours.basicBehaviours import Start, GetSide, CheckTime, SetLoc, GoToLoc, CheckLidar, Stop, SetPosOffset, SetStartPos
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
    from simulation.simulation import SimRobot
    from simulation.communicationSimulation import CommSim as Comm
else:
    from canBus.CommunicationCan import CommunicationCan as Comm

if __name__ == "__main__":
    DISTANCE_CODEUSES = 54
    startPos = Position(420, DISTANCE_CODEUSES, 90)
    ORDER=[2,3,0] #for left side
    TIMEGOBACK= 80 # seconds until robot should start going back to start position
    USELIDAR = True
    USECAMERA = True
    
    logger = logging.getLogger(__name__)
    logger.info("===== Main Program Started =====")
    logger.info(f"Start position: {startPos}, Order: {ORDER}, Go-back time limit: {TIMEGOBACK}s")
    
    if SIMULATION:
        simStartPos = Position(AREA_WIDTH - startPos.x, startPos.y,  startPos.angle)
        simRobot = SimRobot(
        pos=startPos,
        speed=250,
        )
        comm = Comm(simRobot)
    else:
        comm = Comm()
    
    robot = RobotChasseNeige(
        pos=startPos, 
        comm=comm,
        idle_time_buffer=0.5,
        action_timeout=10
    )

    root = py_trees.composites.Sequence("MainSequence", memory=True)
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    root.add_child(SetStartPos(name="set_start_pos", robot=robot, startPos=startPos))
    root.add_child(SetPosOffset(name="set_pos_offset", robot=robot))
    root.add_child(setup(name="setup", order=ORDER, robot=robot))

    sequence_strategie = py_trees.composites.Sequence("sequence_strategie", memory=True)
    
    fallback_lidar = py_trees.composites.Selector("lidar_fallback", memory=True)
    fallback_lidar.add_child(CheckLidar(name="check_time_for_lidar", robot=robot))
    fallback_lidar.add_child(Stop(name="stop_for_lidar", robot=robot))
    
    if USELIDAR:
        sequence_strategie.add_child(fallback_lidar)
    
    procedure_limited_time = py_trees.composites.Sequence("procedure_limited_time", memory=True)
    procedure_limited_time.add_child(CheckTime(name="check_time_under_limit", robot=robot, end_time=TIMEGOBACK))
    procedure_limited_time.add_child(ProcedureNoisette(name="procedure_noisette", robot=robot))

    run_while_time_ok = py_trees.decorators.Repeat(
        name="repeat_procedure_noisette",
        child=procedure_limited_time,
        num_success=len(ORDER),
    )

    sequence_go_back = py_trees.composites.Sequence("sequence_go_back", memory=True)
    sequence_go_back.add_child(SetLoc(name="SetLoc_go_back", robot=robot, loc=Position(150, 100, 90)))
    sequence_go_back.add_child(GoToLoc(name="GoToLoc_go_back", robot=robot))

    fallback = py_trees.composites.Selector("fallback_time", memory=True)
    fallback.add_child(run_while_time_ok)
    fallback.add_child(sequence_go_back)

    sequence_strategie.add_child(fallback)
    
    root.add_child(sequence_strategie)
    
    

    robot.startBT(root, robot)