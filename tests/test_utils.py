import unicodedata

import pytest
from werkzeug.exceptions import Forbidden, NotFound

from brewlog.models import CustomLabelTemplate
from brewlog.utils.brewing import sg2plato, abv
from brewlog.utils.pagination import get_page, url_for_other_page
from brewlog.utils.text import stars2deg, get_announcement
from brewlog.utils.views import get_user_object


class TestTextUtils:

    def test_degree_replacement(self):
        orig_char = '*'
        new_char = unicodedata.lookup('DEGREE SIGN')
        pattern = 'OG was 14%sP, pitch temp. 21%sC'
        text = pattern % (orig_char, orig_char)
        expected = pattern % (new_char, new_char)
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


@pytest.mark.usefixtures('client_class')
class TestViewUtils:

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, label_template_factory):
        self.regular_user = user_factory()
        self.template = label_template_factory(name='custom #1')
        self.template_user = self.template.user

    def test_user_object_objid_none(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.template_user)
        ret = get_user_object(CustomLabelTemplate)
        assert ret is None

    def test_user_object_default_user_raise_403(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.regular_user)
        with pytest.raises(Forbidden):
            get_user_object(CustomLabelTemplate, self.template.id)

    def test_user_object_default_user_no_raise_403(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.regular_user)
        ret = get_user_object(CustomLabelTemplate, self.template.id, raise_403=False)
        assert ret is None

    def test_user_object_default_owner_obj_not_found(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.template_user)
        with pytest.raises(NotFound):
            get_user_object(CustomLabelTemplate, 666)

    def test_user_object_default_owner_ok(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.template_user)
        ret = get_user_object(CustomLabelTemplate, self.template.id)
        assert ret == self.template

    def test_user_object_owner_ok(self, mocker):
        mocker.patch('brewlog.utils.views.current_user', self.regular_user)
        ret = get_user_object(CustomLabelTemplate, self.template.id, user=self.template_user)
        assert ret == self.template
