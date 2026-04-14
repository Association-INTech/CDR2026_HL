#!/usr/bin/env python3

import cv2
from picamera2 import Picamera2
import time
from .TagAruco import TagAruco

timeout = 2.0

# Initialisation caméra
picam2 = Picamera2()
picam2.configure( picam2.create_preview_configuration( main={"format": "RGB888", "size": (1000, 1000) }))
picam2.start()

# Laisse le temps à la caméra de se stabiliser
time.sleep(1)


def gates_setup(color:str, timeout: float=timeout): # notre couleur pour color
    t0 = time.time()
    gates = [0, 0, 0, 0] # s'il n'est pas sûr on prend tout

    while time.time() - t0 < timeout: # limite de temps pour la détection
        frame = picam2.capture_array()   # image en RGB
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        tag_aruco = TagAruco(gray, color)
        tag_aruco.set_gates()
        gates = tag_aruco.gates
        if sum(gates) == 2: # 2 bleus et 2 jaunes
            return gates
    return gates


def shift(gates):
    if sum(gates) == 2:
        if gates[0]:
            if gates[1]:
                return -2  # décale de 2 blocs à gauche
            else:
                return -1  # décale de 1 blocs à gauche
        else:
            if gates[3]:
                if gates[2]:
                    return 2  # décale de 2 blocs à droite 
                else:
                    return 1  # décale de 1 blocs à droite
            else:
                return 0  # reste sur place
    else:
        return 0
            

