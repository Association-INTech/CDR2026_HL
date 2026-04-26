#!/usr/bin/env python3

import logging

import math

from utilities.communicationHardware import CommHardware
from utilities.position import Position

logger = logging.getLogger(__name__)


from canBus.CanBus import CanBus, reg_asserv, reg_action
#import CanBus


class CommunicationCan(CommHardware):
    def __init__(self, reg_type: str ="asserv"):
        super().__init__()
        try:
            self.bus = CanBus(reg_type)
        except Exception as e:
            logger.critical("CAN ERROR: Could not init: %s", e)
            raise e

    def _safe_request(self, command, *args, default=None):
        """CAN request with error handling"""
        try:
            response = self.bus.request(command, *args)
            if response is not None:
                return response

            logger.error("CAN ERROR: Empty response for: %s", command)
        except Exception as e:
            logger.critical("CAN ERROR: Error for %s: %s", command, e)
        
        return default
    
    def switchBus(self, reg_type):
        self.bus = CanBus.CanBus(reg_type)
    #asserv
    
    #send  
    def start_move(self, distance: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("move", -distance)
        logger.debug("CAN: Move command sent: %f", -distance)


    def start_rotate(self, angle: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        #rotate shortest direction
        if angle > 180:
            angle = 180-angle
        angle_rad = angle * math.pi / 180
        self.bus.send("rotate", angle_rad)
        logger.debug("CAN: Rotate command sent: %f rad, %f deg", angle_rad, angle)
    
    def set_position(self, x: float, y: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("set_pos", x, y)
        logger.debug("CAN: Set position command sent: %f, %f", x, y)
        
    
    def stop(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("stop")
        logger.debug("CAN: Stop command sent")

    #request
    def get_feedback(self,id=None):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        logger.debug("CAN: is ildle?: %s", id)
        return self._safe_request("is_idle",default=False)

    
    def get_position(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        
        res = self._safe_request("get_pos")
        if res is None:
            return None 
        x, y, angle = res
        x,y,angle = res
        pos = Position(x, y, angle)
        logger.debug("CAN: get position: %s", pos)
        return pos

    #action

    #send
    #def lift(self):
    #    self.bus.send("lift", ) je sais pas

    #request




