from robot import Robot
from strategieChasseNeige import ProcedurePushNoisetteChasseNeige
from simulation import SimRobot
from position import Position

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    
    simRobot = SimRobot(
        pos=startPos,
        speed=250,
    )
    robot = Robot(pos=startPos, simRobot=simRobot)

    root = ProcedurePushNoisetteChasseNeige("PushNoisette", robot)
    robot.startBT(root, robot)