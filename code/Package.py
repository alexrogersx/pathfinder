from enum import Enum
from datetime import time


class PackageStatus(Enum):
    """
    an Enum to allow for well defined package statuses
    """
    AT_HUB = 1
    IN_TRANSIT = 2
    DELIVERED = 3


class Package:
    def __init__(self, id, location, city, state, zip, deadline, weight, notes, current_time=time(0)):
        self.status = PackageStatus.AT_HUB
        self.status_time = current_time
        self.location = location
        self.id = id
        self.deadline = deadline
        self.city = city
        self.zip = zip
        self.weight = weight
        self.notes = notes
        self.state = state
        self.hub_time = current_time
        self.delivery_time = None
        self.transit_time = None
        self.truck = None

    def __str__(self):
        """
        overrides string method to allow for a human readable string representation of the package object
        :return:
        """
        return str("Package ID: %s\tDestination Address: %s\tSpecial Notes: %s" % (
            self.id, self.location.address, self.notes))


    def set_truck(self, truck):
        self.truck = truck

    def set_delivered(self, time):
        self.status = PackageStatus.DELIVERED
        self.status_time = time
        self.delivery_time = time

    def set_in_transit(self, time):
        self.status = PackageStatus.IN_TRANSIT
        self.status_time = time
        self.transit_time = time

    def set_at_hub(self, time):
        self.status = PackageStatus.AT_HUB
        self.status_time = time
        self.hub_time = time
