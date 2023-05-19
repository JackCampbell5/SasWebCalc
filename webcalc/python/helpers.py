
import json
from json import JSONDecodeError


def encode_json(value=None):
    """Convert value to a JSON string so it can be passed the front-end

    :param dict, list, tuple, string, int, float, bool, none value: - Any value that can be converted to a JSON string. This includes dict, list, tuple, string, int, float, bool, none, amongst others.

    :return: A JSON-encoded string, if successful, otherwise an error related to the object type passed to the method.
    :rtype: str
    """
    try:
        return json.dumps(value)
    except TypeError:
        return f"Unable to convert {type(value).__name__} to JSON string."


def decode_json(value=''):
    """Convert value from a JSON encoded string to a python object

    :param str value:  string that can be converted to a python object.

    :return: A tuple (Object, String) where the object is the decoded python object and the string value is the type of object returned.
    :rtype: Object or String
    """
    try:
        decoded = json.loads(value)
        return decoded, type(decoded).__name__
    except JSONDecodeError:
        return None, f"Unable to convert {value} to python object."
