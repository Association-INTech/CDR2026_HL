#!/usr/bin/env python3

import logging

import math

from utilities.communication import Comm
from utilities.position import Position
from lidar.hokuyo.scan_lidar import run
from gpio_interface.gpio_read import GPIORead

logger = logging.getLogger(__name__)


try:
    from camera.shift import gates_setup, set_gates
except ModuleNotFoundError:
    logger.warning("Camera: import failed")
except Exception as e:
    logger.warning("Camera: failed to setup: %s", e)

from canBus.CanBus import CanBus
#import CanBus



reg_asserv = CanBus.reg_asserv
reg_action = CanBus.reg_action


class CommunicationCan(Comm):
    def __init__(self, reg_type: str ="asserv"):
        super().__init__()
        try:
            self.bus = CanBus(reg_type)
        except Exception as e:
            logger.critical("CAN ERROR: Could not init: %s", e)
            raise e
        try:
            SIDE_SWITCH_PIN = 14
            self.gpio_side_switch = GPIORead(SIDE_SWITCH_PIN)
            TIRETTE_PIN = 20
            self.gpio_tirette = GPIORead(TIRETTE_PIN)
        except Exception as e:
            logger.critical("GPIO ERROR: Could not init: %s", e)
            raise e

    def _safe_request(self, command, *args, default=None):
        """CAN request with error handling"""
        try:
            response = self.bus.request(command, *args)
            if response is not None:
                logger.info(f"response: {repr(response)}")
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
        self.bus.send("move", distance)
        logger.debug("CAN: Move command sent: %f", distance)


    def start_rotate(self, angle: float):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        #angle=angle+45
        #rotate shortest direction
        if angle > 180:
            angle = 180-angle
        angle_rad = angle * math.pi / 180
        self.bus.send("rotate", -angle_rad)
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
        
    def pause(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("pause")
        logger.debug("CAN: Pause command sent")

    def resume(self):
        if self.bus.reg != reg_asserv:
            self.switchBus("asserv")
        self.bus.send("resume")
        logger.debug("CAN: Resume command sent")


    def checkCamera(self, side ):
        color = "yellow" if side else "blue"
        try:
            gates = gates_setup(color)
            logger.debug("Camera: Gates detected: %s", gates)
            return gates if gates is not None else [0, 0, 0, 0]
        except Exception as e:
            logger.error("Camera failure: %s", e)
            return super().checkCamera(side)  # default
        
    def lidar(self, pos):
        try:
            x0,y0,theta = pos.x, pos.y, pos.angle
            is_valid, dist, angle = run(x0,y0,theta)
            THRESHOLD = 400  #TODO test to determine threshold (idk if this is correct)
            logger.debug("LIDAR: is_valid: %s, dist: %smm, angle: %s°", is_valid, dist, angle)
            #if is_valid and dist < THRESHOLD:
            if dist < THRESHOLD:
                logger.info("LIDAR: Obstacle detected, dist: %smm, threshold: %smm", dist, THRESHOLD)
                return True 
            return False        
            
        except Exception as e:
                logger.error("LIDAR failure: %s", e)
                return super().lidar(pos)  # default 


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
    
    def isTierettePulled(self):
        try:
            return not self.gpio_tirette.getPinInput()
        except Exception as e:
            logger.critical("GPIO ERROR: Could not read tirette: %s", e)
            return super().isTierettePulled()  # default


    def getSide(self):
        try:
            return self.gpio_side_switch.getPinInput()
        except Exception as e:
            logger.critical("GPIO ERROR: Could not read side switch: %s", e)
            return super().getSide()  # default

    #action

    #send
    #def lift(self):
    #    self.bus.send("lift", ) je sais pas

    #request




