#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Comm:
    """Classe qui gère la communication avec le LL, on ajoutera les messages CAN ici"""
    #def __init__(self):
    def start_move(self,dist):
        print(f"moved {dist}")
    def start_rotate(self, angle):
        print(f"rotated {angle}")
    def get_position(self):
        return None
    def get_feedback(self,id):
        return True
