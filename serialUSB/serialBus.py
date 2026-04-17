import serial
import time
import logging
import struct

from canBus import CanBus


logger = logging.getLogger(__name__)

reg_asserv = {
    "move" : (0, "<Bd"),
    "rotate" : (1, "<Bd"),
    "set_pos" : (2, "<Bdd"),
    "stop" : (3, "<B"),
    # limite
    "is_idle" : (18, "<B?"),
    "get_pos" : (17, "<Bddd")
}

reg_action = {
    "lift" : (0, "<BBBBB")
}

class SerialBus:

    def __init__(self, reg, port, baudrate: int = 115200, timeout: float = 1.0):
        self.reg=reg
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  
            logger.info("Serial connected to %s", port)
        except Exception as e:
            logger.critical("SERIAL ERROR: Could not init: %s", e)
            raise e
    
    def send(self, msg_name: str, *args):
        """Send a command"""
        msg = self.reg[msg_name] # ajouter if not in reg
        payload = struct.pack(msg[1], msg[0], *args) # erreur de format
        self.ser.write(payload)
        logger.debug("SERIAL SEND: %s", payload)
    
    def request(self, msg_name: str, *args, timeout=1.0):
        """Send a command and wait for a response"""
        msg = self.reg[msg_name]
        payload = struct.pack(msg[1], msg[0], *args)

        self.ser.write(payload) 
        logger.debug("SERIAL SEND: %s", payload)
        
        formate = "<" + msg[1][2:]
        t0 = time.time()
        while time.time() - t0 < timeout:
            payload = self.ser.read()
            if payload:
                logger.debug("SERIAL RECV: %s", payload)
                return struct.unpack(formate, payload)
        logger.error("SERIAL ERROR: Timeout for %s", msg_name)
        return None
