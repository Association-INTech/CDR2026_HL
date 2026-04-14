import logging


logger = logging.getLogger(__name__)


class Comm:
    """Classe qui gère la communication avec le LL, camera, LiDAR, etc..."""
    def __init__(self, startPos):
        self.startPos = startPos
    def start_move(self,dist):
        logger.info("Placeholder: Moved %s", dist)
    def start_rotate(self, angle):
        logger.info("Placeholder: Rotated %s", angle)
    def stop(self):
        logger.info("Placeholder: Stopped")
    def get_position(self):
        logger.info("Placeholder: get_position %s: %s", id, self.startPos)
        return self.startPos
    def get_feedback(self,id=None):
        state = True
        logger.info("Placeholder: Feedback %s: %s", id, state)
        return state
    def putTopBarrier(self,state):
        logger.info("Placeholder: Top Barrier: %s", state)
    def putBottomBarrier(self,state):
        logger.info("Placeholder: Bottom Barrier: %s", state)
    def getSide(self):
        logger.info("Placeholder: getSide %s: %s", id, True)
        return True # True Left (yellow)/ False Right (blue)
    def checkCamera(self,side):
        gates = [0, 0, 0, 0]
        logger.info("Placeholder: checkCamera %s: %s", id, gates)
        return gates
    def lidar(self, pos):
        state = False
        logger.info("Placeholder: Lidar %s: %s", id, state)
        return state
    def tick_simulation(self, tree) -> None:
        return
    def link_frobidden(self, forbidden_zones):
        return

