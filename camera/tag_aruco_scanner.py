#!/usr/bin/env python3

import cv2
from picamera2 import Picamera2
import time


def main():
    # Initialisation caméra
    picam2 = Picamera2()
    picam2.configure( picam2.create_preview_configuration( main={"format": "RGB888", "size": (1000, 1000) }))
    picam2.start()

    # Laisse le temps à la caméra de se stabiliser
    time.sleep(1)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    print("Appuie sur q pour quitter.")

    while True:
        frame = picam2.capture_array()   # image en RGB
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None and len(ids) > 0:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for mid in ids.flatten():
                print("ID détecté :", mid)

        cv2.imshow("ArUco 4x4", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()


main()
