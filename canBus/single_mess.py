#!/usr/bin/env python3

"""
Envoi d'un unique message de 8 octets sur le bus, pour lire le message avec
    un autre CAN, utiliser la commande candump afin de tester la communication
"""

import can

bitrate = 500000

def send_one():
    """
    Envoi un unique message.
    """
    with can.Bus(interface="socketcan", channel="can0", bitrate=bitrate) as bus:
        msg = can.Message(
            arbitration_id=000,
            data=[7, 25, 30, 255, 8, 1, 2, 1],
            is_extended_id=False
        )

        try:
            bus.send(msg)
            print(f"Message envoyé sur {bus.channel_info}")
        except can.CanError:
            print("ERREUR : Message non envoyé")
            

send_one()
