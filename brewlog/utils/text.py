import re
import translitcodec # needed for codec to work at all
import unicodedata

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

_deg_re = re.compile(r'(?<=\d)\*(?=\w\w?\w?)')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))

def stars2deg(text):
    deg_char = unicodedata.lookup('DEGREE SIGN')
    return _deg_re.sub(deg_char, text)
