#!/usr/bin/env python3

import cv2
from cv2 import aruco
from picamera2 import Picamera2
import time


def main():
    # Initialisation caméra
    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={"size": (1200, 1200), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()

    # Laisse le temps à la caméra de se stabiliser
    time.sleep(2)

    # Dictionnaire ArUco 4x4
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    # Paramètres du détecteur
    detector_params = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, detector_params)

    print("Appuie sur q pour quitter.")

    while True:
        # Capture d'une frame depuis Picamera2
        frame = picam2.capture_array()

        # Convertit RGB -> BGR pour OpenCV si besoin d'affichage correct
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Passage en niveaux de gris pour la détection
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Détection des marqueurs
        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is not None and len(ids) > 0:
            # Dessine les tags détectés
            aruco.drawDetectedMarkers(frame_bgr, corners, ids)

            # Affiche l'id et le centre de chaque tag
            for i in range(len(ids)):
                pts = corners[i][0]  # 4 coins du tag
                center_x = int(pts[:, 0].mean())
                center_y = int(pts[:, 1].mean())
                tag_id = int(ids[i][0])

                cv2.circle(frame_bgr, (center_x, center_y), 5, (0, 255, 0), -1)
                cv2.putText(
                    frame_bgr,
                    f"ID: {tag_id}",
                    (center_x + 10, center_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                print(f"Tag detecte : ID={tag_id}, centre=({center_x}, {center_y})")

        # Affichage
        cv2.imshow("Detection ArUco 4x4", frame_bgr)

        # Quitter avec q
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()


if __name__ == "__main__":
    main() 
