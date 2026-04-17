#!/usr/bin/env python3

import logging


from utilities.communication import Comm
from lidar.hokuyo.scan_lidar import run
from gpio_interface.gpio_read import GPIORead

logger = logging.getLogger(__name__)


try:
    from camera.shift import gates_setup, set_gates
except ModuleNotFoundError:
    logger.warning("Camera: import failed")
except Exception as e:
    logger.warning("Camera: failed to setup: %s", e)


class CommHardware(Comm):
    def __init__(self):
        super().__init__()
        TIRETTE_PIN = 20
        SIDE_SWITCH_PIN = 14
        try:
            self.gpio_side_switch = GPIORead(SIDE_SWITCH_PIN)
            self.gpio_tirette = GPIORead(TIRETTE_PIN)
        except Exception as e:
            logger.critical("GPIO ERROR: Could not init: %s", e)
            raise e

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
            x0,y0,theta = pos
            is_valid, dist, angle = run(x0,y0,theta)
            THRESHOLD = 100  #TODO test to determine threshold (idk if this is correct)
            
            if is_valid and dist < THRESHOLD:
                logger.info("LIDAR: Obstacle detected, dist: %smm, threshold: %smm", dist, THRESHOLD)
                return True 
            return False    
            
        except Exception as e:
                logger.error("LIDAR failure: %s", e)
                return super().lidar(pos)  # default 
    
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


