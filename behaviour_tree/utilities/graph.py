from utilities.position import Position
import heapq
import math
import copy
import operator
import logging

logger = logging.getLogger(__name__)


class Graph:
    def __init__(self, size):
        self.size = size
        # self.adjacency_matrix = [[0 for i in range(self.size)] for i in range(self.size)]
        self.adjacency_list = [[] for i in range(self.size)]
        self.weights = {}

    def add_edge(self, a, b, weight):
        # self.adjacency_matrix[a][b]=weight
        if not (isinstance(a, int) and isinstance(b, int)):
            raise ValueError(
                f"Cannot add edge: must be an integer node ID, got {a}, {b}"
            )
        if not b in self.adjacency_list[a]:
            self.adjacency_list[a].append(b)
        self.weights[(a, b)] = weight

    def get_weight(self, a, b):
        # return self.adjacency_matrix[a][b]
        if (a, b) in self.weights:
            return self.weights[(a, b)]
        else:
            return float("inf")

    def get_neighbors(self, node):
        """
        res=[]
        for i in range(self.size):
            if self.get_weight(node,i)!=0:
                res.append((i,self.get_weight(node,i)))
        return res
        """
        return [
            (neighbor, self.weights[(node, neighbor)])
            for neighbor in self.adjacency_list[node]
        ]

    def A_star(self, start, goal, heuristic):

        heap = [(0, start)]
        visited = set()

        g = [float("inf")] * self.size
        g[start] = 0

        f = [float("inf")] * self.size
        f[start] = 0

        visited = [False] * self.size

        parent = [-1] * self.size

        while len(heap) != 0:
            current_f, current = heapq.heappop(heap)

            if visited[current]:
                continue

            visited[current] = True
            if current == goal:
                return (parent, g[goal])

            for neighbor, weight in self.get_neighbors(current):
                if visited[neighbor]:
                    continue
                g_neigbor = g[current] + weight
                if g_neigbor < g[neighbor]:
                    g[neighbor] = g_neigbor
                    f_neighbor = g[neighbor] + heuristic(neighbor, goal)
                    parent[neighbor] = current
                    heapq.heappush(heap, (f_neighbor, neighbor))

        # No path found
        return None, None


class GridGraph(Graph):
    def __init__(self, width, height, scale=1, rotate_buffer=0):
        self.scale = scale
        self.realWidth = width
        self.realHeight = height
        self.width = width // self.scale
        self.height = height // self.scale
        self.NbRotations = 4
        super().__init__(self.width * self.height * self.NbRotations + 1)
        self.setupGrid(rotate_buffer // scale)
        self.backup = copy.deepcopy(self.weights)
        self.forbidden = []

    def setupGrid(self, rotate_buffer):
        forward_speed = 1 * self.scale
        backward_speed = 2 * self.scale
        rotation_speed = 100000
        for x in range(self.width):
            for y in range(self.height):
                for angle in range(self.NbRotations):
                    if (
                        x > rotate_buffer
                        and y > rotate_buffer
                        and self.width - x > rotate_buffer
                        and self.height - y > rotate_buffer
                    ):
                        self.add_edge(
                            self.getNodeID(x, y, angle),
                            self.getNodeID(x, y, (angle + 1) % self.NbRotations),
                            rotation_speed,
                        )
                        self.add_edge(
                            self.getNodeID(x, y, (angle + 1) % self.NbRotations),
                            self.getNodeID(x, y, (angle) % self.NbRotations),
                            rotation_speed,
                        )

                if x < self.width - 1:
                    self.add_edge(
                        self.getNodeID(x, y, round((0 % 360) * self.NbRotations / 360)),
                        self.getNodeID(
                            x + 1, y, round((0 % 360) * self.NbRotations / 360)
                        ),
                        forward_speed,
                    )

                    self.add_edge(
                        self.getNodeID(
                            x + 1, y, round((180 % 360) * self.NbRotations / 360)
                        ),
                        self.getNodeID(
                            x, y, round((180 % 360) * self.NbRotations / 360)
                        ),
                        backward_speed,
                    )

                if y < self.height - 1:
                    self.add_edge(
                        self.getNodeID(
                            x, y, round((90 % 360) * self.NbRotations / 360)
                        ),
                        self.getNodeID(
                            x, y + 1, round((90 % 360) * self.NbRotations / 360)
                        ),
                        forward_speed,
                    )
                    self.add_edge(
                        self.getNodeID(
                            x, y + 1, round((270 % 360) * self.NbRotations / 360)
                        ),
                        self.getNodeID(
                            x, y, round((270 % 360) * self.NbRotations / 360)
                        ),
                        backward_speed,
                    )
        """
        for x in range(self.width-1):
            for y in range(self.height-1):
                self.add_edge(self.getNodeIDFromPos(Position(x,y,0)),self.getNodeIDFromPos(Position(x+1,y,0)),forward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x,y,90)),self.getNodeIDFromPos(Position(x,y+1,90)),forward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x+1,y,180)),self.getNodeIDFromPos(Position(x,y,180)),backward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x,y+1,270)),self.getNodeIDFromPos(Position(x,y,270)),backward_speed)
        """

    def getNodeID(self, x, y, rot):
        id = rot + x * self.NbRotations + y * self.NbRotations * self.width
        return id

    def getNodeIDFromPos(self, pos):
        rot = int((pos.angle % 360) / (360 / self.NbRotations)) % self.NbRotations
        x = int(pos.x // self.scale)
        y = int(pos.y // self.scale)
        if (
            pos.x // self.scale != x
            or pos.y // self.scale != y
            or rot * 360 / self.NbRotations != pos.angle % 360
        ):
            logger.debug(
                f"GRAPH: Position {pos}  approximated to: x {x * self.scale}, y {y * self.scale}, angle {rot * 360 / self.NbRotations}"
            )
        if (
            pos.x < 0
            or pos.x >= self.realWidth
            or pos.y < 0
            or pos.y >= self.realHeight
        ):
            raise ValueError(
                f"Position out of bounds: {pos}, area: {self.realWidth}x{self.realHeight}"
            )
        return self.getNodeID(x, y, rot)

    def getPos(self, id):
        y = id // (self.NbRotations * self.width)
        yr = id % (self.NbRotations * self.width)

        x = yr // self.NbRotations
        xr = yr % self.NbRotations

        angle = xr * 360 / self.NbRotations

        return Position(x * self.scale, y * self.scale, angle)

    def getShortestPath(self, start, goal):
        def heuristic(a, b):
            posa = self.getPos(a)
            posb = self.getPos(b)
            return math.sqrt((posb.x - posa.x) ** 2 + (posb.y - posa.y) ** 2)

        parent, dist = self.A_star(start, goal, heuristic)

        current = goal

        path = [current]
        while current != start:
            current = parent[current]
            path.insert(0, current)
        return path, dist

    def getShortestPathPos(self, startPos, goalPos):
        return [
            self.getPos(id)
            for id in self.getShortestPath(
                self.getNodeIDFromPos(startPos), self.getNodeIDFromPos(goalPos)
            )[0]
        ]

    def getDist(self, startPos, goalPos):
        return self.getShortestPath(
            self.getNodeIDFromPos(startPos), self.getNodeIDFromPos(goalPos)
        )[1]

    def applyForbidden(self, xmin, xmax, ymin, ymax, val):
        for x in range(max(xmin, 0), min(xmax, self.realWidth - 1), self.scale):
            for y in range(max(ymin, 0), min(ymax, self.realHeight - 1), self.scale):
                for angle in range(self.NbRotations):
                    angle_degrees = angle * 360 / self.NbRotations
                    current = self.getNodeIDFromPos(Position(x, y, angle_degrees))
                    neighbors = self.get_neighbors(current)
                    for neighbor, weight in neighbors:
                        original_weight = self.backup.get((current, neighbor), weight)
                        self.add_edge(current, neighbor, val * original_weight)

    def addForbidden(self, xmin, xmax, ymin, ymax, val=1000000, index=None):
        self.applyForbidden(xmin, xmax, ymin, ymax, val)
        if index is None:
            self.forbidden.append((xmin, xmax, ymin, ymax, val))
            return len(self.forbidden) - 1
        else:
            self.forbidden[index] = (xmin, xmax, ymin, ymax, val)
            return index

    def removeForbidden(self, index):
        # self.restore_graph()
        if self.forbidden[index] == None:
            return
        xmin, xmax, ymin, ymax, _ = self.forbidden[index]
        self.forbidden[index] = None
        self.applyForbidden(xmin, xmax, ymin, ymax, 1)

    def get_neighbors(self, node):
        """
        res=[]
        for i in range(self.size):
            if self.get_weight(node,i)!=0:
                res.append((i,self.get_weight(node,i)))
        return res
        """
        return [
            (neighbor, self.weights[(node, neighbor)])
            for neighbor in self.adjacency_list[node]
        ]

    def restore_graph(self):
        self.weights = copy.deepcopy(self.backup)


if __name__ == "__main__":
    test = GridGraph(3000, 2000, scale=10, rotate_buffer=50)
    print("Created Graph")
    print(f"84069 => {test.getPos(84069)}")
    print(f"144041 => {test.getPos(144041)}")
    # print(test.adjency_maxtrix)
    # print(test.getNodeIDFromPos(Position(0,0,0)),test.getNodeIDFromPos(Position(0,0,180)))
    print(
        test.get_weight(
            test.getNodeIDFromPos(Position(0, 0, 0)),
            test.getNodeIDFromPos(Position(0, 0, 90)),
        )
    )
    print(
        test.get_weight(
            test.getNodeIDFromPos(Position(100, 100, 90)),
            test.getNodeIDFromPos(Position(100, 100, 0)),
        )
    )

    # test.addForbidden(500,1000,0,1000)
    # print(test.getShortestPath(test.getNodeIDFromPos(Position(100,0,90)),test.getNodeIDFromPos(Position(2000,1000,90))))
    print(
        [
            f"{pos.x},{pos.y}"
            for pos in test.getShortestPathPos(
                Position(100, 100, 90), Position(100, 100, 0)
            )
        ]
    )
