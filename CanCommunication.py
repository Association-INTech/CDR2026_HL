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

    
    def set_position(self, x: float, y: float):
        return self.bus.send("position", x, y)
        
    
    def stop(self):
        self.bus.send("stop")
    

    def is_idle(self):
        return self.bus.request("is_idle")

    
    def get_position(self):
        return self.bus.request("position")
