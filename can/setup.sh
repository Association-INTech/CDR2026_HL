#! /bin/bash                                                                    

if ip link show can0 | grep -q "can0" ; then
	echo "Le module CAN a été détecté avec succés."
else
	echo "ERREUR : Le module CAN n'a pas été détecté."
	exit 1
fi

sudo ip link set can0 up type can bitrate 250000

sleep 2

ip -details -statistics	link show can0
