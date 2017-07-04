class Flight:
    """Flight information model"""

    def __init__(self, flightno, airline, city, scheduled, expected, status):
        self.flightno = flightno
        self.airline = airline
        self.city = city
        self.scheduled = scheduled
        self.expected = expected
        self.status = status

    def setFlightNo(self, flightno):
        self.flightno = flightno

    def getFlightNo(self):
        return self.flightno

    def setAirline(self, airline):
        self.airline = airline

    def getAirline(self):
        return self.airline

    def setCity(self, city):
        self.city = city

    def getCity(self):
        return self.city

    def setScheduled(self, scheduled):
        self.scheduled = scheduled

    def getScheduled(self):
        return self.scheduled

    def setExpected(self, expected):
        self.expected = expected

    def getExpected(self):
        return self.expected

    def setStatus(self, status):
        self.status = status.lower()

    def getStatus(self):
        return self.status

    def getArray(self):
        """Return an array of flight info"""

        return [self.getFlightNo(),
                self.getAirline(),
                self.getCity(),
                self.getScheduled(),
                self.getExpected(),
                self.getStatus()]
