import re
import unicodedata

_deg_re = re.compile(r'(?<=\d)\*(?=\w\w?\w?)')
_deg_char = unicodedata.lookup('DEGREE SIGN')


def stars2deg(text):
    return _deg_re.sub(_deg_char, text)
