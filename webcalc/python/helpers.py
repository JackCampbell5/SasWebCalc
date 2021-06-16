"""
This python file has a series of helper methods for passing values between the front end javascript
and the backend python.

Methods:

encode_json(value)
    Convert 'value' to a JSON string, if possible, otherwise return an error.

decode_json(value)
    Convert 'value' JSON string to a python object, if possible, otherwise return an error.
"""
import json
from json import JSONDecodeError


def encode_json(value=None):
    """
    Convert value to a JSON string so it can be passed the the front-end

    Arguments:
    value -- Any value that can be converted to a JSON string. This includes dict, list, tuple, string, int, float, bool, none, amongst others.

    Returns a JSON-encoded string, if successful, otherwise an error related to the object type passed to the method.
    """
    try:
        return json.dumps(value)
    except TypeError:
        return f"Unable to convert {type(value).__name__} to JSON string."


def decode_json(value=''):
    """
    Convert value from a JSON encoded string to a python object

    Arguments:
    value -- A string that can be converted to a python object.

    Returns a tuple (Object, String) where the object is the decoded python object and the string value is the type of object returned.
    """
    try:
        decoded = json.loads(value)
        return decoded, type(decoded).__name__
    except JSONDecodeError:
        return None, f"Unable to convert {value} to python object."
