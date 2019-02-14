import unicodedata

import pytest
from werkzeug.exceptions import Forbidden, NotFound

from brewlog.models import BrewerProfile, CustomLabelTemplate
from brewlog.utils.brewing import sg2plato
from brewlog.utils.pagination import get_page, url_for_other_page
from brewlog.utils.text import stars2deg
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


@pytest.mark.usefixtures('client_class')
class TestViewUtils:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.regular_user = BrewerProfile.get_by_email('user@example.com')
        self.template = CustomLabelTemplate.query.filter_by(name='custom #1').first()
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
