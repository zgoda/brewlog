import unicodedata

from brewlog.utils.brewing import sg2plato, abv
from brewlog.utils.pagination import get_page, url_for_other_page
from brewlog.utils.text import stars2deg, get_announcement


class TestTextUtils:

    def test_degree_replacement(self):
        orig_char = '*'
        new_char = unicodedata.lookup('DEGREE SIGN')
        text = f'OG was 14{orig_char}P, pitch temp. 21{orig_char}C'
        expected = f'OG was 14{new_char}P, pitch temp. 21{new_char}C'
        ret = stars2deg(text)
        assert ret == expected

    def test_announcement_not_found(self):
        announcement = get_announcement(None)
        assert announcement is None

    def test_announcement_from_file(self, fs):
        file_name = '/tmp/dummy/announcement.md'
        fs.create_file(file_name, contents='This **very** important announcement.')
        announcement = get_announcement(file_name)
        assert '<strong>very</strong>' in announcement


class TestPaginationUtils:

    def test_get_page_arg_valid(self, mocker):
        request = mocker.Mock(args={'p': '9'})
        assert get_page(request) == 9

    def test_get_page_arg_invalid(self, mocker):
        request = mocker.Mock(args={'p': 'value'})
        assert get_page(request) == 1

    def test_get_page_wrong_arg_name(self, mocker):
        request = mocker.Mock(args={'page': '9'})
        assert get_page(request) == 1

    def test_url_for_other_page(self, mocker, app):
        with app.app_context():
            page = 666
            fake_request = mocker.MagicMock(
                view_args=dict(a1='v1'),
                endpoint='home.index',
            )
            mocker.patch('brewlog.utils.pagination.request', fake_request)
            ret = url_for_other_page(page)
            assert 'p=666' in ret


class TestBrewingFormulas:

    def test_sg2plato(self):
        sg = 1.040
        plato = 10
        assert round(sg2plato(sg)) == plato

    def test_abv(self):
        og = 10
        fg = 2.5
        assert round(abv(og, fg)) == 4
