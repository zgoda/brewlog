import os
import re
import unicodedata

import markdown

_deg_re = re.compile(r'(?<=\d)\*(?=\w\w?\w?)')
_deg_char = unicodedata.lookup('DEGREE SIGN')


def stars2deg(text):
    return _deg_re.sub(_deg_char, text)


def get_announcement(file_name):
    if file_name and os.path.isfile(file_name):
        with open(file_name) as fp:
            return markdown.markdown(fp.read(), safe_mode='remove')
