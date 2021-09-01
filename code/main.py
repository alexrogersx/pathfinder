import copy
from datetime import datetime
from datetime import time
from HashTable import HashTable
from Package import Package
from Package import PackageStatus
from DestinationGraph import DestinationGraph
from DestinationGraph import Location
import csv
from difflib import SequenceMatcher
from PathFinderAlgorithm import PathFinderAlgorithm
from Truck import Truck
from TimeKeeper import TimeKeeper
import re
import random
from UI import UI

"""
Alex Rogers 
Student ID: 003603441
"""


special_packages_delivered_together = set()
special_packages_truck_2 = set()
special_packages_delayed = set()
special_packages_wrong_address = set()

hub_address = '4001 South 700 East'
package_table = HashTable()
destination_graph = DestinationGraph()
all_locations = {}
# Timekeeper used for start of day
time_keeper = TimeKeeper()


def extract_numbers(address):
    """
    extracts numbers from string via regex
    used for comparing similarity between addresses
    :param address: address (string to be searched for numbers )
    :return: a string of extracted numbers
    """
    return re.findall(r'[0-9]+', address)


def search_location(search_term,):
    """
    searches a list of locations for an address, returns address if it is similar enough
    to avoid an unnecessary search, location_list is first directly checked for search_term
    this allows typos to be corrected.
    :param search_term: address to be searched
    :return: found location object
    """
    location_list = all_locations
    found = None
    if search_term in location_list:
        return location_list.get(search_term)
    for item in location_list.keys():
        street_seq = SequenceMatcher(lambda x: x == " ", search_term[5:15], item[5:15])
        number_seq = SequenceMatcher(lambda x: x == " ", extract_numbers(search_term), extract_numbers(item))
        if street_seq.ratio() > 0.3 and number_seq.ratio() > 0.8:
            found = location_list.get(item)
    return found


with open('./assets/distance_table.csv', newline='') as distance_file:
    """
    Parses location information from distance_table.csv
    """
    distance_table = csv.DictReader(distance_file, delimiter=',', skipinitialspace=True, lineterminator='\n',
                                    dialect='excel')
    formatted_locations = []
    # stores locations added. uses additional memory but reduces future iterations to find graph object

    for location in distance_table:
        # stores formatted locations so they can be used in the future
        formatted_location = {}
        # iterate through the location item, format values and adds them to formatted_location
        for key, value in location.items():
            if key == 'name':
                formatted_location['name'] = location.get('name').split('\n')[0].strip()
            elif key == 'address':
                split_location = location.get('address').split('\n')
                formatted_location['address'] = split_location[0].strip()
                if len(split_location) > 1:
                    formatted_location['address_zip'] = split_location[1].strip('(').strip(')')
            else:
                key = key.split('\n')[1].strip().strip(',')
                formatted_location[key] = value.strip()
            if value == 'HUB':
                formatted_location[key] = hub_address
            if key == 'HUB':
                formatted_location[hub_address] = value
        # adds location to destination_graph, this allows a second iteration to loop through and add edges after
        # locations are created
        new_location = Location(formatted_location.get('address', None),
                                formatted_location.get('address_zip', None),
                                formatted_location.get('name', None))

        all_locations[new_location.address] = new_location
        destination_graph.add_location(new_location)
        formatted_locations.append(formatted_location)

    for formatted_location in formatted_locations:
        for key, value in formatted_location.items():
            if key == 'address' or key == 'address_zip' or key == 'name':
                continue
            if value != '':
                destination = search_location(key)
                found_location = search_location(formatted_location.get('address'))
                destination_graph.add_edge(found_location, destination, float(value))

with open('./assets/package_file.csv') as package_file:
    """
    Parses package information from package_file.csv
    """
    package_fieldnames = ['id', 'address', 'city', 'state', 'zip', 'deadline', 'weight', 'notes']
    package_list = csv.DictReader(package_file, delimiter=',', fieldnames=package_fieldnames, skipinitialspace=True)
    for package in package_list:
        if package.get('id').isnumeric():
            deadline = package.get('deadline')
            if deadline == "EOD" or deadline is None:
                deadline = '06:00 PM'
            deadline = datetime.strptime(deadline, '%I:%M %p')
            new_package = Package(int(package.get("id")),
                                  # package.get("address"),
                                  search_location(package.get("address")),
                                  package.get("city"),
                                  package.get('state'),
                                  package.get("zip"), deadline, package.get("weight"),
                                  package.get("notes"),
                                  time_keeper.current_time)
            package_table.insert(new_package)


def get_random_from_list(list_to_select_from):
    """
    selects a random item from a list
    :param list_to_select_from: a list or iterable type which a random candidate is chosen
    :return: the item selected
    """
    return list_to_select_from[random.randint(0, len(list_to_select_from) - 1)]


def find_solution(location_candidates, start_location, path_length=12, calculations=1000):
    """
    Uses a brute force approach with the PathFinderAlgorithm to determine an optimal delivery route given the parameters
    The internal while loop runs until it generates a solution sequence of path_length by running the
    PathFinderAlgorithm against a randomly selected destination location. It stitches multiple PathFinderAlgorithm
    results until it satisfies the path_length requirement. The total distance along the path is calculated, and if
    the distance is shorter than the previous shortest distance, it is stored. The outer algorithm is run a large number
    of times to find a viable solution.

    While the outer loop is not quick, it runs a fixed amount of times and is O(1). The inner loop is O(T)
    (for truck size or truck count). The PathFinderAlgorithm uses Dijkstra's shortest path which runs in O(V^2).
    The overall complexity is O(V^2)

    :param location_candidates: a set of locations to act as potential candidates for stops on a delivery route
    :param start_location: the starting location
    :param path_length: the path length or number of stops for the algorithm to consider defaults to 12
    :param calculations: number of iterations for the brute force algorithm to run defaults to 1000
    :return: the shortest sequence found in the calculations
    """
    shortest_distance = float('inf')
    shortest_sequence = []
    for i in range(calculations):
        current_location = start_location
        destination_sequence = []
        total_distance = 0
        candidates = copy.copy(location_candidates)
        i = 0
        # emulates a do while loop
        while True:
            if not candidates or not len(destination_sequence) <= path_length:
                break
            random_candidate = get_random_from_list(list(candidates))
            algo = PathFinderAlgorithm(destination_graph, current_location, locations=candidates)
            result, distance = algo.calculate_path(random_candidate)
            total_distance += distance
            # [1:] removes the first, which is duplicate of end location in last iteration
            destination_sequence.extend(result[1:])
            candidates.difference_update(set(result))
            current_location = result[len(result) - 1]
            i += 1
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            shortest_sequence = destination_sequence

    return shortest_sequence


def match_packages_to_locations(locations, packages, qty: int, predicate=None):
    """
    finds packages that are to be delivered to the locations supplied
    :param locations: a list of locations to match packages to
    :param packages: a list of packages to choose from
    :param qty: the quantity of packages to return
    :param predicate: an optional predicate to alter the scope of the filter function
    :return: a list made up of packages who's delivery destinations match the supplied locations
    """
    if predicate:
        return list(filter(lambda p: p.location in locations and predicate, packages))[:qty - 1]
    else:
        return list(filter(lambda p: p.location in locations, packages))[:qty - 1]


def determine_solution(package_list, start_location, path_length=16, calculations=1000, package_length=16):
    """
    a parent function to the match_packages_to_locations and find_solution functions.
    maps a list of packages to a list of locations.
    if the find_solution function delivers a solution with more packages than the desired package_length, the
    destinations are looped through adding their respective packages until the package limit has been met. All
    remaining destinations are discarded.
    :param package_list: a list of packages to retrieve locations from
    :param start_location: the start location
    :param path_length: path length to be passed to find_solution
    :param calculations: calculation count to be passed to find_solution
    :param package_length: the total number of packages to be returned
    :return: a delivery path solution based on the given parameters
    """
    location_candidates = set(map(lambda p: p.location, package_list))
    delivery_solution = find_solution(location_candidates, start_location, path_length, calculations)
    matched_packages = match_packages_to_locations(delivery_solution, package_list, 15)
    packages_to_load = []
    delivery_route = []
    if len(matched_packages) > package_length:
        i = 0
        while len(packages_to_load) <= package_length and i < len(delivery_solution) - 1:
            packages_to_load.extend(match_packages_to_locations([delivery_solution[i]],
                                                                package_list,
                                                                package_length - len(packages_to_load)))
            delivery_route.append(delivery_solution[i])
            i += 1

    else:
        packages_to_load = matched_packages
        delivery_route = delivery_solution
    return delivery_route, packages_to_load


def dispatch_truck(truck, delivery_route, packages):
    """
    dispatches a truck and makes deliveries upon a given route
    loops through the trucks delivery_route until all of the packages have been delivered then returns truck to hub
    :param truck: truck to use
    :param delivery_route: a sequence of locations which act as the route for the truck to follow
    :param packages: packages to be loaded onto the truck and delivered
    :return: None
    """
    truck.load(packages)
    while len(truck.get_packages()) > 0:
        for delivery_stop in delivery_route:
            dist = destination_graph.get_distance(truck.current_location, delivery_stop)
            truck.make_delivery_stop(delivery_stop, dist)
    distance_to_hub = destination_graph.get_distance(truck.current_location, search_location(hub_address))

    truck.return_to_hub(distance_to_hub)


def get_remaining_packages():
    """
    filters all packages in package_table that are at the hub to be delivered
    :return: all packages at hub
    """
    # return package_table.filter_packages(lambda x: x.status is not PackageStatus.DELIVERED)
    return package_table.filter_packages(lambda x: x.status is PackageStatus.AT_HUB)


def get_priority_packages():
    """
    filters all priority packages in package_table that are at the hub
    :return: all priority packages at hub
    """
    return package_table.filter_packages(lambda x: x.deadline.time() < time(11) and x.status is PackageStatus.AT_HUB)


def process_special_packages():
    """
    converts a set of package IDs to package objects by using the package_table.search() lookup function
    :return: None
    """
    delivered_together = {13, 14, 15, 16, 19, 20}
    truck_2 = {3, 18, 36, 38}
    delayed = {6, 25, 28, 32}
    # wrong = {9}

    for package_id in truck_2:
        special_packages_truck_2.add(package_table.search(package_id))

    for package_id in delayed:
        special_packages_delayed.add(package_table.search(package_id))

    for package_id in delivered_together:
        special_packages_delivered_together.add(package_table.search(package_id))
    wrong_package = package_table.search(9)
    special_packages_wrong_address.add(wrong_package)

def dispatch_standard_truck(truck):
    """
    dispatches given truck for a standard delivery with no priority or special packages
    :param truck: truck to dispatch
    :return: None
    """
    packages = get_remaining_packages()

    pri_solution, pri_packages = determine_solution(packages, search_location(hub_address), 12, 5000)
    filler_packages = match_packages_to_locations(pri_solution, get_remaining_packages(), 10 - len(packages))
    packages = set(pri_packages).union(set(filler_packages))


    dispatch_truck(truck, pri_solution, packages)


def dispatch_priority_truck(truck):
    """
    dispatches given truck with a priority package load, this is the first truck used
    special packages such as those delayed or required to be delivered on truck two are filtered out.
    :param truck: truck to dispatch
    :return: None
    """
    packages = set(get_priority_packages())
    packages.difference_update(special_packages_truck_2)
    packages.difference_update(special_packages_delayed)
    packages.difference_update(special_packages_wrong_address)
    pri_solution, pri_packages = determine_solution(packages, search_location(hub_address), len(packages), 5000)
    truck.load(packages)
    packages.clear()
    filler_packages = set(match_packages_to_locations(pri_solution, get_remaining_packages(), 16 - len(truck.get_packages())))
    packages.update(filler_packages)

    dispatch_truck(truck, pri_solution, packages)


def dispatch_delayed_priority_truck(truck):
    """
    dispatches truck to deliver delayed priority packages
    multiple sequences of delivery locations are added to this truck.
    priority packages are added to the beginning of the delivery route, next followed by specialty packages required to
    be delivered on truck two. At this stage, additional packages are added whose destinations are already on the
    delivery route. If the truck is not full, an additional route is appended to the delivery route.
    :param truck: truck to dispatch
    :return: None
    """
    packages = set(get_priority_packages())
    special_packages = special_packages_delayed.union(special_packages_truck_2)
    pri_solution, pri_packages = determine_solution(packages, search_location(hub_address), len(packages), 5000)
    special_solution, special_packages = determine_solution(special_packages, pri_solution[-1], len(special_packages),
                                                            5000)
    pri_solution.extend(special_solution)
    packages = set(pri_packages).union(set(special_packages))
    packages.difference_update(special_packages_wrong_address)
    truck.load(packages)
    potential_packages = set(get_remaining_packages()).difference(special_packages_wrong_address)
    packages.clear()
    if len(truck.get_packages()) < 16:
        filler_packages = match_packages_to_locations(pri_solution, potential_packages, 16 - len(packages))
        packages.update(filler_packages[:16 - len(packages)])
        if len(truck.get_packages()) < 16:
            # adds additional stops to route
            target_length = 16 - len(truck.get_packages())-2
            new_solution, new_packages = determine_solution(set(get_remaining_packages())
                                                            .difference(special_packages_wrong_address),
                                                            pri_solution[-1],
                                                            target_length-1,
                                                            5000,
                                                            target_length)
            pri_solution.extend(new_solution)
            packages.update(set(new_packages))

    dispatch_truck(truck, pri_solution, packages)


if __name__ == '__main__':
    process_special_packages()
    print('Please Wait: Calculating Delivery Routes')
    first_truck = Truck('Truck 1', search_location(hub_address), TimeKeeper(time(8)))
    # second_truck starts at 9:15 due to delayed priority packages
    second_truck = Truck('Truck 2', search_location(hub_address), TimeKeeper(time(9, 15)))

    dispatch_priority_truck(first_truck)
    # print(first_truck)
    dispatch_delayed_priority_truck(second_truck)
    # print(second_truck)
    dispatch_standard_truck(second_truck)
    # print(second_truck)
    #
    # print('second_truck', second_truck.get_time())
    # print('first_truck', first_truck.get_time())
    # print('remaining packages', len(get_remaining_packages()))
    # print('first_distance', first_truck.total_distance_traveled)
    # print('second_distance', second_truck.total_distance_traveled)
    print('Calculations Completed')
    ui = UI(package_table, first_truck, second_truck)
    ui.start()

