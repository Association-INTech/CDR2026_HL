#!/usr/bin/env python3

import logging

from math import dist

from behaviour_tree.utilities.communication import Comm
from behaviour_tree.utilities.position import Position
from lidar.hokuyo.scan_lidar import run

logger = logging.getLogger(__name__)


try:
    from camera.shift import gates_setup, set_gates
except ModuleNotFoundError:
    logger.exception("Camera: import failed")
    

from canBus.CanBus import CanBus
#import CanBus



reg_asserv = CanBus.reg_asserv
reg_action = CanBus.reg_action


class CommunicationCan(Comm):
    def __init__(self, startPos, reg_type: str ="asserv"):
        super().__init__(startPos)
        try:
            self.bus = CanBus(reg_type)
        except Exception as e:
            logger.exception("CAN ERROR: Could not init: %s", e)
            raise e
    
    def _safe_request(self, command, *args, default=None):
        """CAN request with error handling"""
        try:
            response = self.bus.request(command, *args)
            if response is not None:
                return response

            logger.error("CAN ERROR: Empty response for: %s", command)
        except Exception as e:
            logger.exception("CAN ERROR: Error for %s: %s", command, e)
        
        return default
    
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
        color = "yellow" if side else "blue"
        try:
            gates = gates_setup(color)
            return gates if gates is not None else [0, 0, 0, 0]
        except Exception as e:
            logger.exception("Camera failure: %s", e)
            return [0, 0, 0, 0] 
        
    def lidar(self, pos):
        try:
            x0,y0,theta = pos
            is_valid, dist, angle = run(x0,y0,theta)
            THRESHOLD = 100  #TODO test to determine threshold (idk if this is correct)
            
            if is_valid and dist < THRESHOLD:
                logger.info("LIDAR: Obstacle detected, dist: %smm, threshold: %smm", dist, THRESHOLD)
                return True 
            return False    
            
        except Exception as e:
                logger.exception("LIDAR failure: %s", e)
                return [0, 0, 0, 0] 


    #request
    def get_feedback(self,id):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        return self.bus._safe_request("is_idle",default=False)

    
    def get_position(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        
        res = self._safe_request("get_pos")
        if res is None:
            return None 
        x, y, angle = res
        x,y,angle = res
        return Position(x, y, angle).add(self.startPos)

    #action

    #send
    #def lift(self):
    #    self.bus.send("lift", ) je sais pas

    #request




