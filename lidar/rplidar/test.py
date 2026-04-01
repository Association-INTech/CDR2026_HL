#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 16:52:29 2026

@author: mn25
"""

from rplidar import RPLidar
import time

baudrate = 256000
timeout = 3
distance_limite = 5000

lidar = RPLidar('/dev/ttyUSB0', baudrate=baudrate, timeout=timeout)

try:
    #print(lidar.get_info())
    #print(lidar.get_health())
    lidar.start_motor()
    time.sleep(1)
    
    #while True:
    for x in lidar.iter_measurments():
        print(f"angle : {x[2]:.2f}, distance = {x[3]}")
        if x[3] < distance_limite:
            print(f"Danger aux abords de {x[2]:.2f}")
            
finally:
    try:
        lidar.stop()
    except:
        pass
    try:
        lidar.stop_motor()
    except:
        pass
    lidar.disconnect()