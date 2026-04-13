import sys
from pathlib import Path

#Fix relative imports
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from behaviour_tree.utilities.logging_setup import setup_logging

setup_logging()

import py_trees
from behaviour_tree.utilities.robot import robotChasseNeige
from behaviour_tree.behaviours.strategieChasseNeige import ProcedureNoisette, setup
from behaviour_tree.behaviours.basicBehaviours import Start, GetSide, CheckTime, SetLoc, GoToLoc
from behaviour_tree.simulation.simulation import SimRobot
from behaviour_tree.utilities.position import Position
from behaviour_tree.utilities.communication import CommSim

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    order=[2,3,0] #for left side
    timeStartGoBack= 80 # seconds until robot should start going back to start position
    
    logger = logging.getLogger(__name__)
    logger.info("===== Main Program Started =====")
    logger.info(f"Start position: {startPos}, Order: {order}, Go-back time limit: {timeStartGoBack}s")
    
    simRobot = SimRobot(
        pos=startPos,
        speed=250,
    )
    comm = CommSim(simRobot)
    robot = robotChasseNeige(pos=startPos, comm=comm)

    root = py_trees.composites.Sequence("MainSequence", memory=True)
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    
    root.add_child(setup(name="setup", order=order, robot=robot))

    procedure_limited_time = py_trees.composites.Sequence("procedure_limited_time", memory=True)
    procedure_limited_time.add_child(CheckTime(name="check_time_under_limit", robot=robot, end_time=timeStartGoBack))
    procedure_limited_time.add_child(ProcedureNoisette(name="procedure_noisette", robot=robot))

    run_while_time_ok = py_trees.decorators.Repeat(
        name="repeat_procedure_noisette",
        child=procedure_limited_time,
        num_success=len(order),
    )

    fallback_go_to_loc = py_trees.composites.Sequence("go_back", memory=True)
    fallback_go_to_loc.add_child(SetLoc(name="SetLoc_go_back", robot=robot, loc=Position(150, 100, 90)))
    fallback_go_to_loc.add_child(GoToLoc(name="GoToLoc_go_back", robot=robot))

    fallback = py_trees.composites.Selector("fallback_time", memory=True)
    fallback.add_child(run_while_time_ok)
    fallback.add_child(fallback_go_to_loc)

    root.add_child(fallback)

    robot.startBT(root, robot)