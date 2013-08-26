from unittest import TestCase

import unicodedata
from brewlog.utils import text as utl


class TextUtilsTests(TestCase):

    def test_degree_replacement(self):
        orig_char = u'*'
        new_char = unicodedata.lookup('DEGREE SIGN')
        pattern = u'OG was 14%sP, pitch temp. 21%sC'
        text = pattern % (orig_char, orig_char)
        expected = pattern % (new_char, new_char)
        ret = utl.stars2deg(text)
        self.assertEquals(ret, expected)
