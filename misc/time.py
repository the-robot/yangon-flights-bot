import re


def twentyfourHour(time):
    """12 hour without mins (i.e. 5pm) to 24 hour format"""

    # if found, FORMAT [(hour, meridiem)]
    time = re.findall(r'(\d+)(am|pm)$', time)

    if not time:  # [] not found
        return None
    elif time[0][1] == "pm":
        return "%02d:00" % (int(time[0][0]) + 12)
    return "%02d:00" % (int(time[0][0]))


def twentyfourHourWithMins(time):
    """12 hour with mins (i.e. 5:45pm) to 24 hour format"""

    # if found, FORMAT [(hour, mins, meridiem)]
    time = re.findall(r'(\d+):(\d+)(am|pm)$', time)

    if not time:  # [] not found
        return None
    elif time[0][2] == "pm":
        return "%02d:%02d" % (int(time[0][0]) + 12, int(time[0][1]))
    return "%02d:%02d" % (int(time[0][0]), int(time[0][1]))


def twelveHour(time):
    """Format 24hr to 12hr time"""
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
        time[0] = "%02d" % hour
        meridiem = "pm"

    return time[0] + ":" + time[1] + meridiem


def isnear(time1, time2):
    """for 24hr format only
       check if times are within 2 hours range difference"""
    
    time1 = [int(x) for x in time1.split(":")]
    time2 = [int(x) for x in time2.split(":")]

    # if hours are same
    if time1[0] == time2[0]:
        return True

    elif abs(int(time1[0]) - int(time2[0])) == 1:
        return True

    return False
