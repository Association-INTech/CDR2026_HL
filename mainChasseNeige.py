import py_trees
from robot import robotChasseNeige
from strategieChasseNeige import ProcedureNoisette, setup
from basicBehaviours import Start, GetSide
from simulation import SimRobot
from position import Position

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    order=[2,3,0] #for left side
    
    
    simRobot = SimRobot(
        pos=startPos,
        speed=250,
    )
    robot = robotChasseNeige(pos=startPos, simRobot=simRobot)

    root = py_trees.composites.Sequence("MainSequence", memory=True)
    root.add_child(Start(name="wait_start_signal", robot=robot))
    root.add_child(GetSide(name="get_side", robot=robot))
    
    root.add_child(setup(name="setup", order=order, robot=robot))

    procedure_noisette = ProcedureNoisette(name="procedure_noisette", robot=robot)
    root.add_child(
        py_trees.decorators.Repeat(
            name="repeat_procedure_noisette",
            child=procedure_noisette,
            num_success=len(order),
        )
    )

    robot.startBT(root, robot)