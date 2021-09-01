class Location:
    """
    Location serves as a vertex in the graph created below
    each location is given an address parameter which will serve as the locations label used in the graph below

    distance and predecessor parameters are used as helpers in the pathfinding algorithm implemented elseware

    distance is initialized to infinity serves as the distance between its predecessor in each iteration of the
    pathfinding algorithm. Predecessor serves as the previous vertex in each iteration.

    name and zipcode are captured for future expansion but not used in algorithm
    name is used in __str__ override
    """

    def __init__(self, address, zipcode=None, name=None):
        self.name = name
        self.zip = zipcode
        self.address = address
        self.distance = float('inf')
        self.predecessor = None
        self.sequence_to_start = []

    def __str__(self):
        if self.name:
            return str('%s %s' % (self.address, self.name))
        return str(self.address)


class DestinationGraph:
    """
    Graph to store all destination data
    locations are vertices and distances are edge weights
    a parameter called edge_weights stores all of the distances as weights between each vertex
    a parameter called adjacency_list stores all of locations as a dict, and the destinations
    reachable from a location as a list, with each destination being a list entry
    """

    def __init__(self):
        self.edge_weights = {}
        self.adjacency_list = {}

    def add_location(self, new_location):
        self.adjacency_list[new_location] = []

    def add_edge(self, origin, destination, distance):
        """
        Adds an edge to a locations list of destinations (adjacency list) and the distance (edge weight) between
        destinations.
        Since edges distances are symmetric, adjacency_list and edge_weights are updated twice with origin and
        destination reversed the second time
        :param origin: Origin location
        :param destination: Destination location
        :param distance: distance between both locations
        :return: None
        """

        self.adjacency_list[origin].append(destination)
        self.adjacency_list[destination].append(origin)
        self.edge_weights[(origin, destination)] = distance
        self.edge_weights[(destination, origin)] = distance

    def get_distance(self, l1, l2):
        return self.edge_weights[(l1,l2)]


