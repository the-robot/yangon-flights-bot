"""
Facebook API Reply Templates
"""

import json


def message(recipient_id, message_text):
    """Normal Message Template"""

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    return data


def options(recipient_id, message_text, options):
    """Message with Quick-Reply Options"""

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies": options
        }
    })

    return data


def list(recipient_id, airlines):
    """List the name of the airlines"""
    
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "elements": airlines
                }
            }
        }
    })

    return data