#!/usr/bin/env python3

from hokuyolx import HokuyoLX
import time
import numpy as np



distance_max = 20000  
distance_min = 20  # En fonction du robot
angle_limit = 125
angle = angle_limit * np.pi / 180
distance_limite = 100
waiting_time = 3 # secondes
incertitude = 10 # millimètre
ref_lidar_angle = -np.pi/2 # orientation du radar par rapport au robot
frequency = 3 # nombre de ratissage pour le boucle != de la fréquence de rotation


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


def coordinatesCalculator(
        x0: float,
        y0:float,
        theta0: float,
        theta:float,
        distance: float
        ) -> tuple:
    absolute_angle = theta0 + theta + ref_lidar_angle
    distance_sup = distance - incertitude # on minimise les riques
    return x0 + distance_sup*np.sin(absolute_angle), y0 + distance_sup*np.cos(absolute_angle)
    


def in_the_field(coordinates: tuple) -> bool:
    for x in coordinates:
        if x < 0:
            return False
    return True



def nearest(scan: np.ndarray) -> tuple:
    """
    Renvoie la distance et l'angle de l'obstacle le plus proche
    """
    distances = [i[1] for i in scan]
    if not distances:
        #print(f"Pas d'obstacle à {distance_max} mm ou le lidar n'a rien capté")
        return 0, float('inf')

    rang = distances.index(min(distances))
    obstacle = scan[rang]
    #print("Obstacle le plus proche :", obstacle[1], "mm")
    #print("Angle (deg) :", obstacle[0] * 180 / np.pi)
    return scan[rang]



def update(laser: HokuyoLX) -> np.ndarray:
    """
    Prend les informations du lidar à l'instant
    """
    try:
        timestamp, scan = laser.get_filtered_dist(dmin=distance_min,dmax=distance_max)
        #print("timestamp :", timestamp) # on s'en fou pour le moment a retravailler
    except Exception as e:
        print("Erreur lors del'update", e)
    return angular_range(scan)
    


def run(x0, y0, theta0) -> None:
    """
    Mise en oeuvre pour l'exécution
    """
    
    try:
        laser = HokuyoLX(addr=("192.168.0.10", 10940), tsync=False)
        laser._convert2ts = lambda ts: decode(ts) #problemes de conversion des timestamp avec la librairie hokuyo
    except Exception as e:
        print("Erreur lors de la création de la classe HokuyoLX", e)
        
    try: # revoir la boucle : tester le temps d'execution
        scan = update(laser)
        theta, distance = nearest(scan)
        coordinates = coordinatesCalculator(x0, y0, theta0, theta, distance)
        print(coordinates)
        return in_the_field(coordinates), distance, theta*180/np.pi
        time.sleep(1e-3)
    finally:
        laser.close()

if __name__ == "__main__":
    # Lancement
    while True:
        try:
            print(run(0,0,0))
        except Exception as e:
            print("Erreur lors du lancement de run()", e)
            time.sleep(1)
            continue
        time.sleep(waiting_time)
