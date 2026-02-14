from position import Position
import heapq

class Graph:
    def __init__(self,size):
        self.size = size
        #self.adjacency_matrix = [[0 for i in range(self.size)] for i in range(self.size)]
        self.adjacency_list = [[]for i in range(self.size)]
        self.weights={}
    
    def add_edge(self,a,b,weight):
        #self.adjacency_matrix[a][b]=weight
        self.adjacency_list[a].append(b)
        self.weights[(a,b)]=weight
    
    def get_weight(self,a,b):
        #return self.adjacency_matrix[a][b]
        if (a,b) in self.weights:
            return self.weights[(a,b)]
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
        return [(neighbor,self.weights[(node,neighbor)]) for neighbor in self.adjacency_list[node]]    
    def A_star(self, start, goal, heuristic):
        
        heap = [(0,start)]
        visited = set()

        g = [float('inf')] * self.size
        g[start]=0

        f = [float('inf')] * self.size
        f[start]=0

        visited = [False] * self.size

        parent=[-1] * self.size

        while len(heap)!=0:
            current_f, current = heapq.heappop(heap) 

            if visited[current]:
                continue

            visited[current]=True
            if current == goal:
                return parent 
            
            for neighbor, weight in self.get_neighbors(current):
                if visited[neighbor]:
                    continue
                g_neigbor = g[current] + weight
                if g_neigbor < g[neighbor]:
                    g[neighbor]=g_neigbor
                    f_neighbor=g[neighbor]+heuristic(start,neighbor)
                    parent[neighbor]=current
                    heapq.heappush(heap, (f_neighbor, neighbor))
        
        #No path found
        return None, None

                

    

class GridGraph(Graph):
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.NbRotations=4
        super().__init__(self.width*self.height*self.NbRotations+1)
        self.setupGrid()
    
    def setupGrid(self):
        foward_speed=1
        backward_speed=2
        rotation_speed=3
        for x in range(self.width):
            for y in range(self.height):
                for angle in range(self.NbRotations):
                    self.add_edge(self.getNodeID(x,y,angle),self.getNodeID(x,y,(angle+1)%self.NbRotations),rotation_speed)
                    self.add_edge(self.getNodeID(x,y,(angle+1)%self.NbRotations),self.getNodeID(x,y,(angle)%self.NbRotations),rotation_speed)

        for x in range(self.width-1):
            for y in range(self.height-1):
                self.add_edge(self.getNodeIDFromPos(Position(x,y,0)),self.getNodeIDFromPos(Position(x+1,y,0)),foward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x,y,90)),self.getNodeIDFromPos(Position(x,y+1,90)),foward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x+1,y,180)),self.getNodeIDFromPos(Position(x,y,180)),backward_speed)
                self.add_edge(self.getNodeIDFromPos(Position(x,y+1,270)),self.getNodeIDFromPos(Position(x,y,270)),backward_speed)

                    
    def getNodeID(self, x, y, rot):
        id=rot+x*self.NbRotations+y*self.NbRotations*self.width
        return id

    def getNodeIDFromPos(self,pos):
        rot=round((pos.angle%360)*self.NbRotations/360)
        return self.getNodeID(pos.x,pos.y,rot)

    def getPos(self,id):
        y = id // (self.NbRotations * self.width)
        yr = id % (self.NbRotations * self.width)

        x = yr // self.NbRotations
        xr = yr % self.NbRotations

        angle = xr * 360 / self.NbRotations

        return Position(x,y,angle)

    def getShortestPath(self,start,goal):
        def heuristic(a,b):
            posa=self.getPos(a)
            posb=self.getPos(b)
            return (posb.x-posa.x)**2+(posb.y-posa.y)**2

        parent=self.A_star(start,goal,heuristic)

        current=goal

        path=[current]
        while current!=start:
            current=parent[current]
            path.insert(0,current)
        return path
        


if __name__ == "__main__":
    test=GridGraph(2000,3000)
    print("Created Graph")
    #print(test.adjency_maxtrix)
    #print(test.getNodeIDFromPos(Position(0,0,0)),test.getNodeIDFromPos(Position(0,0,180)))
    print(test.get_weight(test.getNodeIDFromPos(Position(0,0,0)),test.getNodeIDFromPos(Position(0,0,90))))
    print(test.getShortestPath(test.getNodeIDFromPos(Position(0,0,0)),test.getNodeIDFromPos(Position(100,20,90))))
    