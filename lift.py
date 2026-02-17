import cv2
import time
from AprilTag import AprilTag


cap = cv2.VideoCapture(0)

def lift(color:str, timeout: float = 2.0):
    t0 = time.time()
    gates = [0, 0, 0, 0] # s'il n'est pas sûr on prend tout

    try:
        while time.time() - t0 < timeout: # limite de temps pour la détection
            recorded, frame = cap.read()
            if not recorded:
                continue
            april_tag = AprilTag(frame, color)
            april_tag.set_gates()
            last_gates = april_tag.gates
            if sum(last_gates) == 2: # 2 bleus et 2 jaunes
                return gates
        return gates

    finally:
        cap.release()
        cv2.destroyAllWindows()
