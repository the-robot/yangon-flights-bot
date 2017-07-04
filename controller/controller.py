from datetime import datetime

from model.flights import FlightWrapper
from misc import time


class Flights(FlightWrapper):
    """cli program to test model"""

    def __init__(self):
        # initialize variables
 
        self.current_time = datetime.now()
        self.data = {}  # to store arrival/depart flights

        # retrieve latest flights information
        self.updateArrival()
        self.updateDeparture()

    def search(self, data_type, query):
        """search for the flight information by flight number or airline with time
        @PARAM data_type   -> either 'arrival' or 'departure'
        @PARAM query       -> to look for in flights instances
        """

        flights = []

        if self.initUpdate() is True:
            if data_type == "arrival":
                self.updateArrival()
            else:
                self.updateDeparture()

        for flight in self.data[data_type]:
            if query.upper() in flight.getArray():
                flights.append(flight)

        # if flights not found
        if not flights:
            return []
        return flights

    def searchByTime(self, data_type, query, time_lookup):
        """search for the flight information by flight number or airline with time
        @PARAM data_type   -> either 'arrival' or 'departure'
        @PARAM query       -> to look for in flights instances
        @PARAM time_lookup -> filter results by time
        """

        flights = []

        if self.initUpdate() is True:
            if data_type == "arrival":
                self.updateArrival()
            else:
                self.updateDeparture()

        for flight in self.data[data_type]:
            if query.upper() in flight.getArray() and time.isnear(
                time.twentyfourHour(time_lookup),
                time.twentyfourHourWithMins(flight.getScheduled())):
                flights.append(flight)

        # if flights not found
        if not flights:
            return []
        return flights

    def updateArrival(self):
        """retrieve latest arrival flights information"""

        self.data['arrival'] = self.getArrival()

    def updateDeparture(self):
        """retrieve latest departure flights information"""

        self.data['departure'] = self.getDeparture()

    def compareTime(self, current_time, new_time):
        """return time difference (min, sec) in tuple"""

        difference = new_time - current_time
        return divmod(difference.days * 86400 + difference.seconds, 60)

    def initUpdate(self):
        """determine whether to update flights information or not
        finding difference between current time and last updated time
        must be 5mins difference to retrieve new information"""

        new_time = datetime.now()
        if self.compareTime(self.current_time, new_time)[0] > 5:
            self.current_time = new_time
            return True
        return False