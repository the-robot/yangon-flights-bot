"""
Facebook API Reply Templates
"""

import os
import json


def message(recipient_id, message_text):
    """Normal Message Template"""

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    return params, headers, data


def options(recipient_id, message_text, options):
    """Message with Quick-Reply Options"""

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies": options
        }
    })

    return params, headers, data
