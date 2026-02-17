import cv2
from pupil_apriltags import Detector
import sys # utile ????

"""
modules à télécharger dans la raspi :
https://www.youtube.com/watch?v=tcXYoDxvS3Q
https://www.youtube.com/watch?v=Qf55aUgfLfQ&list=TLPQMTIwMjIwMjbmJSDJmVNkCA&index=2
https://www.youtube.com/watch?v=ZpZozXgtq-o&list=TLPQMTIwMjIwMjbmJSDJmVNkCA&index=1
"""

sys.path.insert(0, "/home/pi/.local/lib/python3.7/site-packages/") # utile ????
cap = cv2.VideoCapture(0)
detector = Detector(families="tag36h11")


while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)

    for tag in tags:
        corners = tag.corners.astype(int)
        tag_id = tag.tag_id

        for i in range(4):
            cv2.line(frame,
                     tuple(corners[i]),
                     tuple(corners[(i+1)%4]),
                     (0,255,0), 2)

        cv2.putText(frame, f"ID {tag_id}",
                    tuple(corners[0]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0,0,255), 2)

    cv2.imshow("AprilTag", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
