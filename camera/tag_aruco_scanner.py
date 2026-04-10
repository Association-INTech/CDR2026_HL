#!/usr/bin/env python3

import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.configure(
    picam2.create_video_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
)
picam2.start()

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

while True:
    frame = picam2.capture_array()   # image en RGB
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(frame_bgr, corners, ids)
        for mid in ids.flatten():
            print("ID détecté :", mid)

    cv2.imshow("ArUco 4x4", frame_bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
