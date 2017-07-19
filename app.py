import os
import sys

import requests
from flask import Flask, request

from controller.controller import Flights
from view import templates
from misc import time
from misc import lang
from misc import emoji


flights = Flights()
app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # log incoming message

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]

                    try:
                        message_text = messaging_event["message"]["text"]
                    except KeyError:
                        emojiPerserving(sender_id)

                        message = u"I can only read sentences."
                        data = templates.message(sender_id, message)
                        send(data)
                    else:
                        incomingHandler(sender_id, message_text)
    return "ok", 200


def incomingHandler(sender_id, message_text):
    """handle incoming text messages, and pass to replyHandler"""

    # make sure the messsage only contains english characters
    if not lang.isEnglish(message_text):
        # send poker face
        emojiPoker(sender_id)

        message = u"I can only speak in english."
        data = templates.message(sender_id, message)
        send(data)

    else:
        # check if there is time in message
        # FORMAT: <query> around <time in 12hr> (i.e. 7pm)
        message_text = message_text.rsplit(" around ", 1)

        # time not included search by flight no. or airline
        if len(message_text) == 1:
            if message_text[0].upper() == "AIRLINES":
                airlines = u"This is the list of airlines"
                for each in flights.getAirlines():
                    airlines += u"\n\u2022 " + unicode(each)
                data = templates.message(sender_id, airlines)
                send(data)

            else:
                arrivals = flights.search('arrival', message_text[0])
                departures = flights.search('departure', message_text[0])
                replyHandler(sender_id, message_text[0], arrivals, departures)

        # if time included, len is 2
        else:
            message = message_text[0]
            # change time to 24 hour format
            time_in_24hr = time.twentyfourHour(message_text[1])

            if time_in_24hr is not None:
                arrivals = flights.searchByTime('arrival', message_text[0], time_in_24hr)
                departures = flights.searchByTime('departure', message_text[0], time_in_24hr)
                replyHandler(sender_id, message_text[0], arrivals, departures)
            else:
                # send persevering emoji
                emojiPerserving(sender_id)

                # send error message, for time format error
                message = u"Sorry, your time is not valid, it should be 12hr format without minutes. (i.e. 7pm)"
                data = templates.message(sender_id, message)
                send(data)


def replyHandler(sender_id, query, arrivals, departures):
    """Message Handler. reply the text based on the searched result contidion
    @PARAM sender_id  -> client user id
    @PARAM query      -> what user is looking for
    @PARAM arrivals   -> searched result of flights based on query
    @PARAM departures -> searched result of flights based on query
    """

    # searched flight information
    searched_flights = arrivals + departures

    # if flight not found
    if len(searched_flights) == 0:
        message = u"Sorry, I cannot find any flight with {}.".format(query.title())
        data = templates.message(sender_id, message)
        send(data)

        # Send Sorry Emoji
        emojiSorry(sender_id)

    # if flight is in arrivals
    elif len(searched_flights) == 1 and departures == []:
        message = u"Flight {} operated by {} from {} will arrive at {}. It's {}.".format(
                   searched_flights[0].getFlightNo(), searched_flights[0].getAirline().title(),
                   searched_flights[0].getCity(), searched_flights[0].getScheduled(),
                   searched_flights[0].getStatus().lower())
        data = templates.message(sender_id, message)
        send(data)

    # if flight is in departures
    elif len(searched_flights) == 1 and arrivals == []:
        message = u"Flight {} operated by {} to {} will take off at {}.".format(
                   searched_flights[0].getFlightNo(), searched_flights[0].getAirline().title(),
                   searched_flights[0].getCity(), searched_flights[0].getScheduled())
        data = templates.message(sender_id, message)
        send(data)

    # if there are more than 1 matched flights and it is less than 11
    elif len(searched_flights) > 1 and len(searched_flights) <= 11:
        # same flight numbers exists in arrivals data
        if len(arrivals) > 1 and not departures and flights.sameFlightNumbers(arrivals):
            message = u"There are {} flights.".format(len(arrivals))
            data = templates.message(sender_id, message)
            send(data)

            # loop and show all flights info
            for each in searched_flights:
                message = u"Flight {} operated by {} from {} will arrive at {}. It's {}.".format(
                           each.getFlightNo(), each.getAirline().title(),
                           each.getCity(), each.getScheduled(),
                           each.getStatus().lower())
                data = templates.message(sender_id, message)
                send(data)

        # same flight numbers exist in departure data
        elif len(departures) > 1 and not arrivals and flights.sameFlightNumbers(departures):
            message = u"There are {} flights.".format(len(departures))
            data = templates.message(sender_id, message)
            send(data)

            # loop and show all flights info
            for each in searched_flights:
                message = u"Flight {} operated by {} to {} will take off at {}.".format(
                           each.getFlightNo(), each.getAirline().title(),
                           each.getCity(), each.getScheduled())
                data = templates.message(sender_id, message)
                send(data)

        # ask user to choose by flight number
        # (Facebook quick replies maximum limit is 11)
        else:
            options = []
            for flight in searched_flights:
                options.append({
                    "content_type": "text",
                    "title": flight.getFlightNo(),
                    "payload": flight.getFlightNo()
                    })
            data = templates.options(sender_id,
                u"Please select the flight number {}".format(emoji.grinning),
                options)
            send(data)

    else:
        message = u"There are many flights with {}. {}".format(
                   query.title(), emoji.grinning)
        data = templates.message(sender_id, message)
        send(data)

        # show list of flight numbers of given airline
        # add to sets to remove duplicate flight numbers
        flightNumbers = set()
        for each in searched_flights:
            flightNumbers.add((each.getFlightNo(), each.getScheduled()))

        message = u"Flight Numbers: "
        for each in flightNumbers:
            message += u"\n\u2022 {0:>7}, {1:>7}".format(
                unicode(each[0]),
                unicode(each[1]))
        data = templates.message(sender_id, message)
        send(data)


def send(data):
    """send data back to client"""
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
            params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


# Fancy Methods
def emojiSorry(sender_id):
    message = u"{} {} {} {}".format(
        emoji.sorry, emoji.sorry, emoji.sorry, emoji.sorry)
    data = templates.message(sender_id, message)
    send(data)

def emojiPerserving(sender_id):
    message = u"{}".format(emoji.persevering)
    data = templates.message(sender_id, message)
    send(data)

def emojiPoker(sender_id):
    message = u"{}".format(emoji.poker)
    data = templates.message(sender_id, message)
    send(data)


if __name__ == '__main__':
    app.run(debug=True)
