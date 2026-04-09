#! /bin/bash


# Se placer dans le répertoire du code
cd /home/intech/Bureau/cdr/CDR2026_HL # à revoir


# Activer l'environnement virtuel qui contient toutes les bibliothèques
source venv/bin/activate


# Configurer le CAN
./can/setup_can.sh


# Configurer le lidar
./lidar/hokuyo/setup_lidar.sh
# Lancer le scan en arrière-plan
./lidar/hokuyo/scan_lidar.py


#camera