from hokuyolx import HokuyoLX
import time
import numpy as np



distance_max = 20000
distance_min = 20
angle_limit = 125
angle = angle_limit * np.pi / 180
distance_limite = 100



def angular_range(scan: np.ndarray):
    """
    Filtre la plage angulaire utile
    """
    l = []
    for i in range(len(scan)):
        if scan[i,0] < -angle or scan[i,0] > angle:
            continue
        else:
            l.append(scan[i])
    return np.array(l)



def decode(ts: str):
    """
    Décodeur en base 64
    """
    value = 0
    for c in ts:
        value = (value << 6) + (ord(c) - 48)
    return value



def nearest(scan: np.ndarray) -> None:
    """
    Affiche la distance et l'angle de l'objet le plu proche
    """
    distances = [i[1] for i in scan]
    if not distances:
        print(f"Pas d'objet à {distance_max} mm")
        return False

    rang = distances.index(min(distances))
    objet = scan[rang]

    print("Obstacle le plus proche :", objet[1], "mm")
    print("Angle (deg) :", objet[0] * 180 / np.pi)
    return objet[1] < distance_limite



def update(laser: HokuyoLX) -> np.ndarray:
    """
    Prend les informations du lidar à l'instant
    """
    timestamp, scan = laser.get_filtered_dist(dmin=distance_min,dmax=distance_max)
    scan = angular_range(scan)
    print("timestamp :", timestamp)
    return nearest(scan)
    
    


def run() -> None:
    """
    Mise en oeuvre pour l'exécution
    """
    laser = HokuyoLX(addr=("192.168.0.10", 10940), tsync=False)
    laser._convert2ts = lambda ts: decode(ts) #problemes de conversion des timestamp avec la librairie hokuyo

    try:
        for _ in range(10):
            if update(laser):
                pass # lancer stop
            time.sleep(0.1)
    finally:
        laser.close()

while True:
    try:
        run()
    except Exception as e:
        print("Erreur :", e)
        time.sleep(1)
