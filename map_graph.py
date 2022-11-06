from queue import PriorityQueue


class MapGraph:
    def __init__(self):
        self.graph = {}
    
    def add_point(self, point, neighbors):
        self.graph[point] = neighbors
    
    def neighbors(self, point):
        return self.graph[point]
    
    def FromMapString(map_string):      # X-wall O - path
        map_graph = MapGraph()
        map_matrix = MapGraph.create_and_verify_map_matrix(map_string)

        for j in range (len(map_matrix)):
            for i in range(len(map_matrix[0])):
                if (map_matrix[j][i] == "O"):
                    neighbors = []
                    if (j > 0):
                        if (map_matrix[j-1][i] == "O"):
                            neighbors.append((i, j - 1))
                    else:
                        if (map_matrix[len(map_matrix) - 1][i] == "O"):
                            neighbors.append((i, len(map_matrix) - 1))

                    if (j < len(map_matrix) - 1):
                        if (map_matrix[j + 1][i] == "O"):
                            neighbors.append((i, j + 1))
                    else:
                        if (map_matrix[0][i] == "O"):
                            neighbors.append((i, 0))

                    if (i > 0):
                        if (map_matrix[j][i - 1] == "O"):
                            neighbors.append((i - 1, j))
                    else:
                        if (map_matrix[j][len(map_matrix[0]) - 1] == "O"):
                            neighbors.append((len(map_matrix[0]) - 1, j))

                    if (i < len(map_matrix[0]) - 1):
                        if (map_matrix[j][i + 1] == "O"):
                            neighbors.append((i + 1, j))
                    else:
                        if (map_matrix[j][0] == "O"):
                            neighbors.append((0, j))

                    map_graph.add_point((i, j), neighbors)

        return map_graph          
    
    def create_and_verify_map_matrix(map_string):
        map_matrix = map_string.split("\n")

        first_line_length = len(map_matrix[0])

        for line in map_matrix:
            if (len(line) != first_line_length):
                print("Oh no, line ", line, " is garbage!")
                return []
        
        return map_matrix

    def get_shortest_path(self, start, finish):
        came_from = self.build_shortest_path(start, finish)
        return MapGraph.trace_shortest_path(came_from, start, finish)
    
    def build_shortest_path(self, start, finish):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if (current == finish):
                break
            
            for next_move in self.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_move not in cost_so_far or new_cost < cost_so_far[next_move]:
                    cost_so_far[next_move] = new_cost
                    priority = new_cost + MapGraph.manhattan_distance(next_move, finish)
                    frontier.put(next_move, priority)
                    came_from[next_move] = current
        
        return came_from
    
    def manhattan_distance(point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
    
    
    def trace_shortest_path (came_from, start, finish):
        reverse_path = [finish]
        current = finish

        while (current != start):
            current = came_from[current]
            reverse_path.append(current)
        
        reverse_path.reverse()

        return reverse_path