#!/usr/bin/env python3

import cv2



cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids: # affichage de l'ID sur l'écran
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        for mid in ids.flatten():
            print("ID détecté :", mid)

    cv2.imshow("ArUco 4x4", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
