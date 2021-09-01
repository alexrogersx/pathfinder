from DestinationGraph import Location
import copy


class Truck:
    def __init__(self, name, hub_location, time_keeper):
        self.name = name
        self.packages = set()
        self.package_limit = 16
        self.distance_from_hub = 0
        self.current_location = hub_location
        self.hub_location = hub_location
        self.distance_traveled_on_trip = 0
        self.total_distance_traveled = 0
        self.internal_timeline = copy.deepcopy(time_keeper)
        self.last_delivery_size = None

    def load(self, *new_packages):
        """
        loads packages
        initializes data variables related to a trucks trip
        takes one or multiple new_packages to be added to truck
        :param new_packages: packages to load onto truck
        :return: None
        """
        self.distance_traveled_on_trip = 0
        self.current_location = self.hub_location
        new_packages = set(new_packages[0])
        for new_package in new_packages:
            new_package.set_in_transit(self.internal_timeline.current_time)
        if len(self.packages) + len(new_packages) <= self.package_limit:
            self.packages = self.packages.union(new_packages)
            self.last_delivery_size = len(self.packages)
            return
        raise Exception(str('not enough capacity in truck. Tried %s , capacity is %s   %s' % (
            len(self.packages) + len(new_packages), self.package_limit, self.name)))

    def deliver_package(self):
        """
        delivers packages
        finds packages that are local to trucks current location
        sets package status to delivered
        :return: None
        """
        local_packages = set(filter(lambda x: x.location is self.current_location, self.packages))
        for package in local_packages:
            package.set_delivered(self.internal_timeline.current_time)
            package.set_truck(self.name)
        self.packages = self.packages - local_packages
        # print(str('delivering %s packages' % (len(local_packages)) ))

    def travel_to_location(self, next_location, travel_distance):
        """
        totals the distance traveled on trip for statistic use
        advances internal timeline by travel distance
        :param next_location: the location to travel to and make the delivery
        :param travel_distance: the distance to travel to next_location
        :return: None
        """
        self.internal_timeline.advance_time(travel_distance)
        self.distance_traveled_on_trip += travel_distance
        self.current_location = next_location

    def make_delivery_stop(self, next_location, travel_distance):
        """
        initiates a chain of events around delivering a package
        calls travel_to_location function
        calls deliver_package function

        :param next_location: the location to travel to and make the delivery
        :param travel_distance: the distance to travel to next_location
        :return:None
        """
        if type(next_location) is Location and next_location is not self.current_location:
            self.travel_to_location(next_location, travel_distance)
            self.deliver_package()
            return True
        return False

    def return_to_hub(self, travel_distance):
        """
        returns truck to hub, adds distance to trip
        :param travel_distance: distance to the hub
        :return:
        """
        self.travel_to_location(self.hub_location, travel_distance)
        self.total_distance_traveled += self.distance_traveled_on_trip

    def get_time(self):
        """
        returns the trucks internal timeline
        :return: current_time object
        """
        return self.internal_timeline.current_time

    def get_packages(self):
        """
        converts set of package to list
        :return: list of package
        """
        return list(self.packages)

    def get_total_distance(self):
        """
        :return: total distance traveled by truck
        """
        return self.total_distance_traveled

    def get_limit(self):
        """
        :return: trucks package limit
        """
        return self.package_limit

    def __str__(self):
        """
        converts truck to human readable string
        :return:
        """
        return str('Truck: %s\n'
                   '\tTotal Distance Last Trip: %s\n'
                   '\tCurrent Time: %s \n'
                   '\tLast Delivery Size %s' % (
                       self.name, self.distance_traveled_on_trip, self.get_time(), self.last_delivery_size))
