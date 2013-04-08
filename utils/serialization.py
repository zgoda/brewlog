import time

def serialize_datetime(value):
    ms = time.mktime(value.utctimetuple())
    ms += getattr(value, 'microseconds', 0) / 1000
    return int(ms)
