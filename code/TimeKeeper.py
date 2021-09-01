import datetime
from datetime import time
from datetime import timedelta
from datetime import date
from datetime import datetime


class TimeKeeper:
    """
    acts as the time keeping for the project
    has helper functions for converting distance to time
    """
    def __init__(self, start_time=time(6)):
        d = date.today()
        self.current_time = datetime.combine(d, start_time)

    def advance_time(self, distance):
        miles_to_minutes = timedelta(minutes=round(distance * 60/18))
        self.current_time += miles_to_minutes

    def __str__(self):
        return str('The current time is %s' % self.current_time)
