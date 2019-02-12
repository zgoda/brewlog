import urllib
import datetime

from flask import url_for
import pytest

from brewlog.models.brewing import Brew
from brewlog.models.brewery import Brewery

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBrewery(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.public_brewery = Brewery.query.filter_by(name='brewery #1').first()
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1').first()

    def test_nonowner_view_list(self):
        """
        Hidden breweries can not be seen by non owner
        """
        url = url_for('brewery.all')
        self.login(self.client, self.public_brewery.brewer.email)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert self.hidden_brewery.name not in content
        assert url_for('brewery.delete', brewery_id=self.public_brewery.id) in content

    def test_owner_view_list(self):
        """
        Owner of hidden brewery can see it on the list
        """
        url = url_for('brewery.all')
        self.login(self.client, self.hidden_brewery.brewer.email)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert self.hidden_brewery.name in content
        assert url_for('brewery.delete', brewery_id=self.hidden_brewery.id) in content

    def test_anon_view_list(self):
        url = url_for('brewery.all')
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert self.hidden_brewery.name not in content
        assert self.public_brewery.name in content
        assert url_for('brewery.delete', brewery_id=self.public_brewery.id) not in content

    def test_nonowner_view(self):
        """
        View by ordinary user:
            * only basic information if public
            * 404 if hidden
        """
        rv = self.client.get(url_for('brewery.details', brewery_id=self.public_brewery.id))
        content = rv.data.decode('utf-8')
        assert self.public_brewery.name in content
        assert 'action="%s"' % self.public_brewery.absolute_url not in content
        rv = self.client.get(url_for('brewery.details', brewery_id=self.hidden_brewery.id))
        assert rv.status_code == 404

    def test_owner_view(self):
        """
        View by logged in user, owner of one of the breweries:
            * only basic information in non-owned
            * form in owned, even if hidden
        """
        self.login(self.client, self.hidden_brewery.brewer.email)
        rv = self.client.get(url_for('brewery.details', brewery_id=self.public_brewery.id))
        content = rv.data.decode('utf-8')
        assert self.public_brewery.name in content
        assert 'action="%s"' % self.public_brewery.absolute_url not in content
        rv = self.client.get(url_for('brewery.details', brewery_id=self.hidden_brewery.id))
        assert '<form' in rv.data.decode('utf-8')

    def test_nonowner_change(self):
        """
        Change data by non owner:
            * 403
        """
        self.login(self.client, self.hidden_brewery.brewer.email)
        url = url_for('brewery.details', brewery_id=self.public_brewery.id)
        rv = self.client.post(url, data={'name': 'new name'})
        assert rv.status_code == 403

    def test_owner_change(self):
        """
        Change data by owner:
            * success
        """
        self.login(self.client, self.hidden_brewery.brewer.email)
        url = url_for('brewery.details', brewery_id=self.hidden_brewery.id)
        new_name = 'new name'
        rv = self.client.post(url, data={'name': new_name}, follow_redirects=True)
        assert rv.status_code == 200
        assert new_name in rv.data.decode('utf-8')
        brewery = Brewery.query.get(self.hidden_brewery.id)
        assert brewery.name == new_name

    def test_owner_access_delete_form(self):
        url = url_for('brewery.delete', brewery_id=self.hidden_brewery.id)
        self.login(self.client, self.hidden_brewery.brewer.email)
        rv = self.client.get(url)
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_owner_delete(self):
        """
        Delete brewery by owner:
            * success
        """
        brewery_id = self.hidden_brewery.id
        self.login(self.client, self.hidden_brewery.brewer.email)
        url = url_for('brewery.delete', brewery_id=self.hidden_brewery.id)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 200
        assert Brewery.query.get(brewery_id) is None

    def test_nonowner_delete(self):
        """
        Delete brewery by non owner:
            * 403
        """
        self.login(self.client, self.hidden_brewery.brewer.email)
        url = url_for('brewery.delete', brewery_id=self.public_brewery.id)
        rv = self.client.post(url, data={'delete_it': True})
        assert rv.status_code == 403

    def test_add_form_visible_for_registered(self):
        url = url_for('brewery.add')
        self.login(self.client, self.public_brewery.brewer.email)
        rv = self.client.get(url)
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_create_logged_in_user(self):
        self.login(self.client, self.public_brewery.brewer.email)
        data = {
            'name': 'new brewery',
            'description': 'new brewery in town',
            'established_date': datetime.datetime.utcnow().strftime('%Y-%m-%d')
        }
        url = url_for('brewery.add')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert data['name'] in rv.data.decode('utf-8')

    def test_create_anon(self):
        data = {
            'name': 'new brewery',
        }
        url = url_for('brewery.add')
        redirect_url = url_for('auth.select') + '?%s' % urllib.parse.urlencode({'next': url})
        rv = self.client.post(url, data=data, follow_redirects=False)
        assert redirect_url in rv.headers.get('Location')


@pytest.mark.usefixtures('client_class')
class TestBreweryBrews(BrewlogTests):

    """
    List of brews from single brewery:
        * owner sees everything
        * others see only public brews
        * if brewery is hidden others get 404
    """

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.public_brewery = Brewery.query.filter_by(name='brewery #1').first()
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1').first()

    def test_owner_view(self):
        url = url_for('brewery.brews', brewery_id=self.public_brewery.id)
        hidden_brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        self.login(self.client, self.public_brewery.brewer.email)
        rv = self.client.get(url)
        assert hidden_brew.name in rv.data.decode('utf-8')

    def test_public_view(self):
        url = url_for('brewery.brews', brewery_id=self.public_brewery.id)
        hidden_brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        self.login(self.client, self.hidden_brewery.brewer.email)
        rv = self.client.get(url)
        assert hidden_brew.name not in rv.data.decode('utf-8')

    def test_hidden_view_by_public(self):
        url = url_for('brewery.brews', brewery_id=self.hidden_brewery.id)
        self.login(self.client, self.public_brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 404
