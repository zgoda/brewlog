# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import codecs
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
        with codecs.open(file_name, encoding='utf-8') as fp:
            return markdown.markdown(fp.read(), safe_mode='remove')
