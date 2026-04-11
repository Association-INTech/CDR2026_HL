#!/usr/bin/env python3

import time
import struct
import can
import isotp

reg_asserv = {
    "move" : (0, "<Bd"),
    "rotate" : (1, "<Bd"),
    "set_pos" : (2, "<Bdd"),
    "stop" : (3, "<B"),
    "is_idle" : (16, "<B?"),
    "get_pos" : (17, "<Bddd")
}

reg_action = {
    "lift" : (0, "<BBBBB")
}

limite = 16 # de 0 à 16 les messages de send et à partir de 16 request

class CanBus:

    def __init__(self, reg_type: str, can_channel="can0", bitrate=250000):
        if reg_type == "asserv":
            self.tx = 0x1
            self.rx = 0x2
            self.reg = reg_asserv
        elif reg_type == "action":
            self.tx = 0x3
            self.rx = 0x4
            self.reg = reg_action
        else:
            raise Exception("ArgError : Le bus est soit en asserv ou en action.")
        self.can_channel = can_channel
        self.bitrate = bitrate
        # ouvre le bus CAN socketcan
        self.bus = can.Bus(interface="socketcan", channel=can_channel, bitrate=bitrate)
        # adresse sur 11 bits avec tx et rx
        self.addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=self.tx, rxid=self.rx)
        # paramétres du protocole ISOTP
        self.isotp_params = { 
            "stmin": 5, # délai entre CF (ms)
            "blocksize": 8, # nombre de CFs entre les FC
            "wftmax": 0, # wait frames max (0 = désactivé)
            # "tx_padding": 0x00, # padding si besoin # ?????
            "rx_flowcontrol_timeout": 1000, # ms
            "rx_consecutive_frame_timeout": 1000, # ms
        }
        # création de la stack ISOTP
        self.stack = isotp.CanStack(
            bus=self.bus,
            address=self.addr,
            params=self.isotp_params,
            error_handler=lambda e: print("[ISO-TP ERROR]", e),
        )
        


    def close(self) -> None:
        self.bus.shutdown()

    def send(self, msg_name: str, *args, timeout=1.0) -> None:
        """
        Envoi un message et attend la fin de l'envoi.
        """
        msg = self.reg[msg_name] # ajouter if not in reg
        payload = struct.pack(msg[1], msg[0], *args) # erreur de format
        self.stack.send(payload)

        t0 = time.time()
        while time.time() - t0 < timeout:
            self.stack.process()
            if not self.stack.transmitting():
                return None
            time.sleep(1e-5)

        raise TimeoutError("Timeout : Envoi non terminé. Délai dépassé")
    
    def request(self, msg_name: str, timeout=1.0):
        """
        Fait une requête et attend la réponse.
        """
        msg = self.reg[msg_name] # ajouter if not in reg
        payload = struct.pack("<B", msg[0]) # erreur de format
        self.stack.send(payload)

        t0 = time.time()
        while time.time() - t0 < timeout:
            self.stack.process()
            if not self.stack.transmitting():
                break
            time.sleep(1e-5)

        
        formate = "<" + msg[1][2:]
        t0 = time.time()
        while time.time() - t0 < timeout:
            self.stack.process()
            while self.stack.available():
                payload = self.stack.recv()
                return struct.unpack(formate, payload) # erreur de format
            time.sleep(1e-5)

        raise TimeoutError("Timeout : Retour non reçu. Délai dépassé")
