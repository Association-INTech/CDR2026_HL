import cv2
import time
from TagAruco import TagAruco



cap = cv2.VideoCapture(0, cv2.CAP_V4L2)



def lift(color:str, timeout: float = 2.0): # notre couleur pour color
    t0 = time.time()
    gates = [0, 0, 0, 0] # s'il n'est pas sûr on prend tout

    while time.time() - t0 < timeout: # limite de temps pour la détection
        recorded, frame = cap.read()
        if not recorded:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tag_aruco = TagAruco(gray, color)
        tag_aruco.set_gates()
        gates = tag_aruco.gates
        if sum(gates) == 2: # 2 bleus et 2 jaunes
            return gates
    return gates
