from communication import Communication
import CanBus

class CommunicationCan(Communication):
    def __init__(self, reg_type: str):
        super().__init__()
        self.bus = CanBus.CanBus(reg_type)
        
    #asserv
    
    #send  
    def start_move(self, distance: float):
        self.bus.send("move", distance)


    def start_rotate(self, angle: float):
        self.bus.send("rotate", angle)

    
    def set_position(self, x: float, y: float):
        return self.bus.send("set_pos", x, y)
        
    
    def stop(self):
        self.bus.send("stop")

    
    #request
    def is_idle(self):
        return self.bus.request("is_idle")

    
    def get_position(self):
        return self.bus.request("get_pos")

    #action

    #send
    #def lift(self):
    #    self.bus.send("lift", ) je sais pas

    #request




