import numpy as np
import cv2
from pupil_apriltags import Detector

detector = Detector(families="tag36h11")


def tri(liste: list) -> None:
    for i in range(1,4):
        j = i
        while j > 0:
            if liste[j][0] < liste[j-1][0]:
                liste[j-1], liste[j] = liste[j], liste[j-1]
            else:
                break
            j -= 1
            

class AprilTag:

    def __init__(self, image:np.ndarray, color:str):
        if color == "yellow":
            self.opponent_id = 2
        elif color == "blue":
            self.opponent_id = 1
        else:
            self.opponent_id = False
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.tags = detector.detect(self.gray)
        self.gates = [0, 0, 0, 0]

    def set_gates(self) -> None:
        if len(self.tags) == 4: # si les 4 tags ne sont pas détectés il recommence
            id_place = []
            for tag in self.tags:
                corners = tag.corners.astype(int)
                id_place.append([corners[0,1],tag.tag_id])
            tri(id_place)
            for i in range(4):
                if id_place[i][1] == self.opponent_id: # à adapter
                    self.gates[i] = 1
