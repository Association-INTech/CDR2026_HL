from communication import Communication
import CanBus

class CommunicationCan(Communication):
    def __init__(self, reg_type: str):
        super().__init__()
        self.bus = CanBus.CanBus(reg_type)
    

    def move(self, distance: float):
        self.bus.send("move", distance)


    def rotate(self, angle: float):
        self.bus.send("rotate", angle)


    def position(self, ):
        return self.bus.request("position")
    

    def is_idle(self):
        return self.bus.request("is_idle")
