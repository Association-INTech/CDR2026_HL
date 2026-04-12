#!/usr/bin/env python3


import numpy as np
import cv2



aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)



def tri(liste: list) -> None:
    for i in range(1,4):
        j = i
        while j > 0:
            if liste[j][0] < liste[j-1][0]:
                liste[j-1], liste[j] = liste[j], liste[j-1]
            else:
                break
            j -= 1



class TagAruco:

    def __init__(self, gray:np.ndarray, color:str):
        if color == "yellow":
            self.opponent_id = 36
        elif color == "blue":
            self.opponent_id = 47
        else:
            self.opponent_id = -1 # on prend tout
        self.gates = [0, 0, 0, 0]
        self.tags = []

        corners, ids, _ = detector.detectMarkers(gray)
        if ids is not None and len(ids) > 0:
            for i in range(len(ids)):
                self.tags.append((corners[i][0][0][1],ids[i][0])) #verticalement


    def set_gates(self) -> None:
        if len(self.tags) == 4: # si les 4 tags ne sont pas tous détectés il recommence 
            tri(self.tags)
            for i in range(4):
                if self.tags[i][1] == self.opponent_id:
                    self.gates[i] = 1
