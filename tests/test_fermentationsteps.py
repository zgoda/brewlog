import datetime

import pytest
from flask import url_for

from brewlog.models import FermentationStep

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestFermentationSteps(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory, brew_factory, fermentation_step_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user, name='public brewery no 1')
        self.public_brew = brew_factory(brewery=self.public_brewery, name='public brew no 1')
        self.fstep = fermentation_step_factory(brew=self.public_brew, og=12.5, volume=21, name='primary')
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user, name='hidden brewery no 1')
        self.hidden_brew = brew_factory(brewery=self.hidden_brewery, name='hidden brew no 1')

    def test_add_fermentation_step_by_owner(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.hidden_brew.id)
        self.login(self.hidden_user.email)
        data = {
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
            'name': 'secondary',
        }
        rv = self.client.get(url_for('brew.details', brew_id=self.hidden_brew.id))
        content = rv.data.decode('utf-8')
        assert '<h3>%s</h3>' % self.hidden_brew.full_name in content
        assert data['name'] not in content
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert data['name'] in rv.data.decode('utf-8')

    def test_add_fermentation_step_by_public(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.hidden_user.email)
        data = {
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
            'name': 'secondary',
        }
        rv = self.client.get(url_for('brew.details', brew_id=self.public_brew.id))
        assert '<h3>%s</h3>' % self.public_brew.full_name in rv.data.decode('utf-8')
        assert data['name'] not in rv.data.decode('utf-8')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 403

    def test_add_fermentation_step_to_nonexisting_brew(self):
        brew_id = 666
        url = url_for('ferm.fermentationstep_add', brew_id=brew_id)
        self.login(self.hidden_user.email)
        data = {
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
            'name': 'primary',
        }
        rv = self.client.get(url_for('brew.details', brew_id=brew_id))
        assert rv.status_code == 404
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 404

    def test_delete_fermentation_step(self):
        fstep_id = self.fstep.id
        url = url_for('ferm.fermentationstep_delete', fstep_id=fstep_id)
        self.login(self.public_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        content = rv.data.decode('utf-8')
        assert rv.status_code == 200
        assert '<h3>%s</h3>' % self.public_brew.full_name in content
        assert url not in content
        assert FermentationStep.query.get(fstep_id) is None

    def test_delete_fermentation_step_by_public(self):
        fstep_id = self.fstep.id
        url = url_for('ferm.fermentationstep_delete', fstep_id=fstep_id)
        self.login(self.hidden_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 403

    def test_delete_fermentation_step_owner_sees_form(self):
        url = url_for('ferm.fermentationstep_delete', fstep_id=self.fstep.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_edit_fermentation_step_owner_sees_form(self):
        url = url_for('ferm.fermentation_step', fstep_id=self.fstep.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert self.fstep.name in rv.data.decode('utf-8')

    def test_edit_fermentation_step_owner_can_modify(self):
        url = url_for('ferm.fermentation_step', fstep_id=self.fstep.id)
        self.login(self.public_user.email)
        data = {
            'name': 'primary (mod)',
            'date': self.fstep.date.strftime('%Y-%m-%d'),
            'og': self.fstep.og,
            'fg': self.fstep.fg,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert data['name'] in rv.data.decode('utf-8')

    def test_edit_fermentation_step_by_public(self):
        url = url_for('ferm.fermentation_step', fstep_id=self.fstep.id)
        self.login(self.hidden_user.email)
        data = {
            'name': 'primary (mod)',
            'date': self.fstep.date.strftime('%Y-%m-%d'),
            'og': self.fstep.og,
            'fg': self.fstep.fg,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 403

    def test_set_og_sets_fg(self, fermentation_step_factory):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.public_user.email)
        date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'secondary',
            'og': 2.5,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        step = FermentationStep.query.filter_by(brew=self.public_brew, name=data['name']).first()
        prev_step = FermentationStep.query.filter_by(brew=self.public_brew).order_by(FermentationStep.date).first()
        assert prev_step.fg == step.og

    def test_set_fg_changes_og(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.public_user.email)
        date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data_secondary = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'secondary',
            'og': 3,
            'notes': 'secondary fermentation',
        }
        rv = self.client.post(url, data=data_secondary, follow_redirects=True)
        assert rv.status_code == 200
        url = url_for('ferm.fermentation_step', fstep_id=self.fstep.id)
        data_primary = {
            'name': 'primary (mod)',
            'date': self.fstep.date.strftime('%Y-%m-%d'),
            'og': self.fstep.og,
            'fg': 2,
        }
        rv = self.client.post(url, data=data_primary, follow_redirects=True)
        assert rv.status_code == 200
        next_step = FermentationStep.query.filter_by(name=data_secondary['name']).first()
        assert next_step.og == data_primary['fg']

    def test_set_og_changes_fg(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.public_user.email)
        date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data_secondary = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'secondary',
            'og': 3,
            'notes': 'secondary fermentation',
        }
        rv = self.client.post(url, data=data_secondary, follow_redirects=True)
        assert rv.status_code == 200
        assert FermentationStep.query.filter_by(brew=self.public_brew).count() == 2
        step = FermentationStep.query.filter_by(brew=self.public_brew, name=data_secondary['name']).first()
        url = url_for('ferm.fermentation_step', fstep_id=step.id)
        data = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'secondary',
            'og': 2.5,
            'notes': 'secondary fermentation',
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        prev_step = FermentationStep.query.filter_by(brew=self.public_brew).order_by(FermentationStep.date).first()
        assert prev_step.fg == data['og']

    def test_insert_step_with_fg(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.public_user.email)
        date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        data = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'pre-primary',
            'og': 12,
            'fg': 3,
            'notes': 'starter',
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        step = FermentationStep.query.filter_by(name=self.fstep.name).first()
        assert step.og == data['fg']

    def test_complete_fermentation_display(self):
        url = url_for('ferm.fermentationstep_add', brew_id=self.public_brew.id)
        self.login(self.public_user.email)
        date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        data_secondary = {
            'date': date.strftime('%Y-%m-%d'),
            'name': 'secondary',
            'og': 3,
            'fg': 2.5,
            'notes': 'secondary fermentation',
        }
        rv = self.client.post(url, data=data_secondary, follow_redirects=True)
        assert rv.status_code == 200
        assert '5.5%' in rv.data.decode('utf-8')
