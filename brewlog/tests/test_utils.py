from unittest import TestCase
import unicodedata

import mock

from brewlog.utils.models import get_page
from brewlog.utils.text import stars2deg


class TextUtilsTestCase(TestCase):

    def test_degree_replacement(self):
        orig_char = u'*'
        new_char = unicodedata.lookup('DEGREE SIGN')
        pattern = u'OG was 14%sP, pitch temp. 21%sC'
        text = pattern % (orig_char, orig_char)
        expected = pattern % (new_char, new_char)
        ret = stars2deg(text)
        self.assertEqual(ret, expected)


class ModelUtilsTestCase(TestCase):

    def setUp(self):
        self.request = mock.MagicMock()

    def test_pagination_arg_valid(self):
        self.request.args = {'p': '9'}
        self.assertEqual(get_page(self.request), 9)

    def test_pagination_arg_invalid(self):
        self.request.args = {'p': 'value'}
        self.assertEqual(get_page(self.request), 1)

    def test_pagination_wrong_arg_name(self):
        self.request.args = {'page': '9'}
        self.assertEqual(get_page(self.request), 1)
