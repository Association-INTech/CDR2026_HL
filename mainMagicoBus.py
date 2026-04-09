from robot import robotMagicoBus
from strategieMagicoBus import ProcedurePushNoisetteMagicoBus
from simulation import SimRobotMagicoBus
from position import Position

if __name__ == "__main__":
    startPos = Position(150, 100, 90)
    
    simRobot = SimRobotMagicoBus(
        pos=startPos,
        speed=250,
    )
    robot = robotMagicoBus(pos=startPos, simRobot=simRobot)

    root = ProcedurePushNoisetteMagicoBus("PushNoisette", robot)
    robot.startBT(root, robot)