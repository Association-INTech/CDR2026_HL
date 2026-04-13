#!/usr/bin/env python3


from behaviour_tree.utilities.communication import Communication
from camera.shift import set_gates
from lidar.hokuyolx.scan_lidar import run

import CanBus



reg_asserv = CanBus.reg_asserv
reg_action = CanBus.reg_action

class CommunicationCan(Communication):
    def __init__(self, reg_type: str):
        super().__init__()
        self.bus = CanBus.CanBus(reg_type)
    
    def switchBus(self, reg_type):
        self.bus = CanBus.CanBus(reg_type)
    #asserv
    
    #send  
    def start_move(self, distance: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("move", distance)


    def start_rotate(self, angle: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("rotate", angle)

    
    def set_position(self, x: float, y: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("set_pos", x, y)
        
    
    def stop(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("stop")

    def checkCamera(self, side ):
        if side:
            side = "yellow"
        else:
            side = "blue"
	return gates_setup(side)

    def lidar(x0,y0,theta):
        return run(x0,y0,theta)

    #request
    def is_idle(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        return self.bus.request("is_idle")

    
    def get_position(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        return self.bus.request("get_pos")

    #action

    #send
    #def lift(self):
    #    self.bus.send("lift", ) je sais pas

    #request




