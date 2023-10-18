import json


def load_msg_data(message):
    try:
        return json.loads(message.data)
    except (TypeError, ValueError):
        return None
