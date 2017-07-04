import os
import sys
import json

import requests
from flask import Flask, request

from controller.controller import Flights
from view import templates
from misc import time


# create flights instant
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
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    # make sure the messsage only contains english characters
                    if not isEnglish(message_text):
                        message = "Sorry, I can only speak in english for now."
                        params, headers, data = templates.message(sender_id, message)
                        send(params, headers, data)

                    else:
                        # check if there is time in message (FORMAT: query at time)
                        message_text = message_text.rsplit(" around ", 1)

                        # time not included search by flight no. or airline 
                        if len(message_text) == 1:
                            arrivals = flights.search('arrival', message_text[0])
                            departures = flights.search('departure', message_text[0])
                            handler(sender_id, message_text[0], arrivals, departures)
                        # if time included, len should be 2
                        else:
                            message = message_text[0]
                            # change time to 24 hour format
                            time_in_12hr = time.twentyfourHour(message_text[1])

                            if time_in_12hr is not None:
                                arrivals = flights.searchByTime('arrival', message_text[0], time_in_12hr)
                                departures = flights.searchByTime('departure', message_text[0], time_in_12hr)
                                handler(sender_id, message_text[0], arrivals, departures)
                            else:
                                # send error message, for time format error
                                message = "Sorry, your time is not valid, it should be 12hr\
                                           format without minutes. (i.e. 7pm)"
                                params, headers, data = templates.message(sender_id, message)
                                send(params, headers, data)
    return "ok", 200


def handler(sender_id, query, arrivals, departures):
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
        message = "Sorry, I cannot any flights with {}".format(query.title())
        params, headers, data = templates.message(sender_id, message)

    # if flight is in arrivals
    elif len(searched_flights) == 1 and departures == []:
        message = "Flight {} from {} will arrive at {}. It's {}.".format(
                   searched_flights[0].getFlightNo(), searched_flights[0].getCity(),
                   searched_flights[0].getScheduled(), searched_flights[0].getStatus().lower())
        params, headers, data = templates.message(sender_id, message)

    # if flight is in departures
    elif len(searched_flights) == 1 and arrivals == []:
        message = "Flight {} to {} will take off at {}.".format(
                   searched_flights[0].getFlightNo(), searched_flights[0].getCity(),
                   searched_flights[0].getScheduled())
        params, headers, data = templates.message(sender_id, message)

    # if there are more than 1 matched flights and it is less than 11
    # ask user to choose by flight number
    # (Facebook quick replies maximum limit is 11)
    elif len(searched_flights) > 1 and len(searched_flights) <= 11:
        options = []
        for flight in searched_flights:
            options.append({
                "content_type": "text",
                "title": flight.getFlightNo(),
                "payload": flight.getFlightNo()
                })
        params, headers, data = templates.options(sender_id, "Please select the flight number", options)

    # TODO
    else:
        message = "Sorry, there are many flights with {}. Please give me the flight number or tell me the time. I.e. 'Air KBZ around 6pm'".format(
                   query.title())
        params, headers, data = templates.message(sender_id, message)
    
    send(params, headers, data)


def send(params, headers, data):
    """send data back to client"""

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


def isEnglish(word):
    """check if given input is in English"""

    try:
        word.decode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


if __name__ == '__main__':
    app.run(debug=True)
