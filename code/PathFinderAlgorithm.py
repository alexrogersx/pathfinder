

class PathFinderAlgorithm:
    def __init__(self, graph, start_location, **locations):
        """
        Implements Dijkstra's shortest path algorithm
        runs in 0(V^2) time where V vertices are locations
        :param graph: a graph data structure storing the data to be processed
        :param start_location: starting location used to calculate the distance to
        :param locations: a subset of the locations inside of the graph which are used to narrow the search
        """
        self.start_location = start_location
        self.graph = graph

        found_not_visited = []
        for location in self.graph.adjacency_list:
            # checks if location is currently in package list
            if locations and location in locations:
                found_not_visited.append(location)
            location.distance = float('inf')
            location.predecessor = None

        self.start_location.distance = 0

        # while found_not_visited has a positive length
        while len(found_not_visited):
            shortest_distance_index = 0
            # loops through to find the shortest index
            for i in range(1, len(found_not_visited)):
                if found_not_visited[i].distance < found_not_visited[shortest_distance_index].distance:
                    shortest_distance_index = i
            current_location = found_not_visited.pop(shortest_distance_index)

            # checks potential next stops for shortest distance
            for possible_stop in self.graph.adjacency_list[current_location]:
                distance_to_possible_stop = self.graph.edge_weights[(current_location, possible_stop)]
                total_distance_from_start = current_location.distance + distance_to_possible_stop

                # checks if current calculated distance from start to location is shorter than its current stored
                # distance. if so, that known distance is updated to the current calculated distance.

                if total_distance_from_start < possible_stop.distance:
                    possible_stop.distance = total_distance_from_start
                    possible_stop.predecessor = current_location
                    possible_stop.sequence_to_start.append(current_location)

    def calculate_path(self, end_location):
        """
        calculates the shortest path from the start location specified in the constructor to the end_location
        :param end_location: the end location to find the shortest distance to
        :return: a tuple of:
                calculated_path: a sequence of paths calculated to be the shortest distance between start location and
                end_location
                total_distance: the total distance between between start location and end_location
        """
        calculated_path = []
        current_location = end_location
        total_distance = 0
        # traverse path in opposite order by adding locations predecessors
        while current_location and current_location != self.start_location:
            calculated_path.append(current_location)
            current_location = current_location.predecessor
        # reverse calculated_path to reflect actual order of traversed path
        calculated_path.reverse()
        # insert original path
        calculated_path.insert(0, self.start_location)
        for i in range(0, len(calculated_path) - 1):
            total_distance += self.graph.edge_weights[(calculated_path[i], calculated_path[i + 1])]
        return calculated_path, total_distance
