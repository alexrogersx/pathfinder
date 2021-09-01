from datetime import datetime
from datetime import date
from HashTable import HashTable
from Package import Package
from Truck import Truck


class UI:
    def __init__(self, package_table: HashTable, first_truck: Truck, second_truck: Truck):
        self.package_table = package_table
        self.first_truck = first_truck
        self.second_truck = second_truck
        self.menu = "Welcome to WGUPS\n" \
                    "Please select from the following menu options:\n" \
                    "1: Get total truck distance\n" \
                    "2: Check status by time\n" \
                    "X: Exit"
        self.total_distance = round(self.first_truck.get_total_distance() + self.second_truck.get_total_distance())
        self.total_distance_message = 'Total Distance Traveled = %s \n' % self.total_distance
        self.check_status_message = 'Enter a time to check status in 24 hour format HHMM (i.e 1430 is 2:30pm)'

    def start(self):
        while True:
            print(self.menu)
            menu_input = input().strip()
            if menu_input.lower() == 'x':
                break
            elif '1' in menu_input:
                print(self.total_distance_message)
            elif '2' in menu_input:
                print(self.check_status_message)
                parsed_time = None
                while True:
                    try:
                        time_input = input().strip()
                        if time_input.lower() == 'menu':
                            break
                        parsed_time = datetime.combine(date.today(), datetime.strptime(time_input, '%H%M').time())
                        break
                    except ValueError:
                        print('Invalid time entered please try again')
                        print('Enter \'menu\' to return to main menu')
                if parsed_time is None:
                    continue
                packages = self.package_table.get_all_packages()
                for package in packages:
                    package: Package
                    if package.transit_time > parsed_time and package.delivery_time > parsed_time:
                        status_message = str(
                            '\tStatus: Arrived at the hub at: %s' % package.hub_time.strftime('%H:%M%p'))
                    elif package.delivery_time > parsed_time > package.transit_time:
                        status_message = str(
                            '\tStatus: In transit for delivery. Departed Hub at: %s' % package.transit_time.strftime('%H:%M%p'))
                    else:
                        status_message = str('\tStatus: Delivered at: %s by %s'
                                             % (package.delivery_time.strftime('%H:%M%p'), package.truck))
                    print('Package ID: %s %s' % (package.id, status_message))

