import codecs
import os
import re
import unicodedata

import markdown

_deg_re = re.compile(r'(?<=\d)\*(?=\w\w?\w?)')
_deg_char = unicodedata.lookup('DEGREE SIGN')


def stars2deg(text: str) -> str:
    return _deg_re.sub(_deg_char, text)


def get_announcement(file_name: str) -> str:
    if file_name and os.path.isfile(file_name):
        with codecs.open(file_name, encoding='utf-8') as fp:
            return markdown.markdown(fp.read())
