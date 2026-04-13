class Comm:
    """Classe qui gère la communication avec le LL, camera, LiDAR, etc..."""
    def __init__(self, startPos):
        self.startPos = startPos
    def start_move(self,dist):
        print(f"moved {dist}")
    def start_rotate(self, angle):
        print(f"rotated {angle}")
    def stop(self):
        print("stopped")
    def get_position(self):
        return self.startPos
    def get_feedback(self,id):
        return True
    def putTopBarrier(self,state):
        print(f"Top Barrier: {state}")
    def putBottomBarrier(self,state):
        print(f"Bottom Barrier: {state}")
    def getSide(self):
        return True # True Left (yellow)/ False Right (blue)
    def checkCamera(self,side):
        gates = [0, 0, 0, 0]
        return gates
    def tick_simulation(self, tree) -> None:
        return

