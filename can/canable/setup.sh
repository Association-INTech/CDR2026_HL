#! /bin/bash

num=$1
if [ -z $num ]; then
    num=0
fi

empl="/dev/ttyACM$num"

if ! ls /dev/ttyACM* | grep -q $empl ; then
    echo "ERREUR : $empl n'est pas occupé"
    exit 1
fi

sudo slcand -o -c -s4 $empl can0 # configure le canable sur la cananl "can0"
sleep 1

sudo ip link set can0 up type can bitrate 500000 # active "can0" bitrate à 500000
sleep 1

ip -details -statistics	link show can0 # affiche les stats de can0

