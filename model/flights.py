import urllib2
from bs4 import BeautifulSoup

from . import useragents
from .model import Flight


class FlightWrapper:
    """Class to retrieve flight [arrival/departure] informations"""

    def getArrival(self):
        """return array of flight objects of arrival flights"""

        arrivalurl = "https://www.airportia.com/burma/yangon-international-airport/arrivals"
        arrivalqueries = ['FlightNo', 'Airline', 'From', 'Scheduled', 'Expected', 'status']
        return self.getFlights(self.getHtml(arrivalurl), arrivalqueries)

    def getDeparture(self):
        """return array of flight objects of departure flights"""

        departurl = "https://www.airportia.com/burma/yangon-international-airport/departures"
        departqueries = ['FlightNo', 'Airline', 'To', 'Scheduled', 'Expected', 'status']
        return self.getFlights(self.getHtml(departurl), departqueries)

    def getHtml(self, url):
        """return html byte code of given url"""

        try:
            req = urllib2.Request(url, headers=useragents.get())
            connection = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            #print(e.code)  # FOR DEBUG
            return None
        except urllib2.URLError as e:
            #print(e.code)  # FOR DEBUG
            return None
        return connection.read()

    def getFlights(self, html, queries):
        """scrape juicy info from html

        Parameters:
            html -- html byte code
            queries -- name of quicy info to look for inside html
        """

        # flights[] will store flight() objects
        flights = []
        soup = BeautifulSoup(html, "html.parser")

        # scrape by each row
        for row in soup.find_all('tr'):
            columns = [row.find('td', class_=queries[0]),
                       row.find('td', class_=queries[1]),
                       row.find('td', class_=queries[2]),
                       row.find('td', class_=queries[3]),
                       row.find('td', class_=queries[4]),
                       row.find('td', class_=queries[5])]

            # add if all columns are not empty
            if any(column for column in columns):
                # format city name, remove city code
                city = columns[2].find('a')['title'].split(" ")
                city.remove(city[-2])

                flight = Flight(columns[0].find('a').text.upper(),
                                columns[1].find('a').text.upper(),
                                " ".join(word for word in city),
                                self.meridiemFormat(columns[3].text),
                                self.meridiemFormat(columns[4].text),
                                columns[5].find('div').text)
                flights.append(flight)
        return flights

    def meridiemFormat(self, time):
        """ Format 24hr to 12hr time """
        time = time.split(":")

        if not any(time):
            return u''

        elif time[0] == "00":
            time[0] = "12"
            meridiem = "am"

        elif int(time[0]) < 12:
            meridiem = "am"

        elif int(time[0]) == 12:
            meridiem = "pm"

        elif int(time[0]) > 12:
            hour = int(time[0]) - 12
            if hour >= 10:
                time[0] = str(hour)
            else:
                time[0] = "0" + str(hour)
            meridiem = "pm"

        return time[0] + ":" + time[1] + meridiem