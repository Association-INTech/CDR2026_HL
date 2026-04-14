#! /bin/bash


# Activer l'environnement virtuel qui contient toutes les bibliothèques
source venv/bin/activate


# Configurer le CAN
./canBus/setup_can.sh


# Configurer le lidar
./lidar/hokuyo/setup_lidar.sh


./behaviour_tree/mainChasseNeige.py
