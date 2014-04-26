import datetime

from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models.brewing import Brew, FermentationStep
from brewlog.models.users import BrewerProfile


class FermentationStepsTestCase(BrewlogTestCase):

    def setUp(self):
        super(FermentationStepsTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.fstep = FermentationStep.query.filter_by(brew=self.brew).first()
        self.another_user = BrewerProfile.get_by_email('user2@example.com')

    def test_add_fermentation_step_by_owner(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'secondary',
            }
            rv = client.get(url_for('brew-details', brew_id=self.brew.id))
            self.assertIn('<h3>%s</h3>' % self.brew.full_name.encode('utf-8'), rv.data)
            self.assertNotIn(data['name'], rv.data)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['name'], rv.data)

    def test_add_fermentation_step_by_public(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.another_user.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'secondary',
            }
            rv = client.get(url_for('brew-details', brew_id=self.brew.id))
            self.assertIn('<h3>%s</h3>' % self.brew.full_name.encode('utf-8'), rv.data)
            self.assertNotIn(data['name'], rv.data)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_add_fermentation_step_to_nonexisting_brew(self):
        brew_id = 666
        url = url_for('brew-fermentationstep_add', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'primary',
            }
            rv = client.get(url_for('brew-details', brew_id=brew_id))
            self.assertEqual(rv.status_code, 404)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 404)

    def test_delete_fermentation_step(self):
        fstep_id = self.fstep.id
        url = url_for('brew-fermentationstep_delete', fstep_id=fstep_id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>%s</h3>' % self.brew.full_name.encode('utf-8'), rv.data)
            self.assertNotIn(url, rv.data)
            self.assertIsNone(FermentationStep.query.get(fstep_id))

    def test_edit_fermentation_step_owner_sees_form(self):
        url = url_for('brew-fermentation_step', fstep_id=self.fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(self.fstep.name.encode('utf-8'), rv.data)

    def test_edit_fermentation_step_owner_can_modify(self):
        url = url_for('brew-fermentation_step', fstep_id=self.fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            data = {
                'name': 'primary (mod)',
                'date': self.fstep.date.strftime('%Y-%m-%d'),
                'og': self.fstep.og,
                'fg': self.fstep.fg,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['name'].encode('utf-8'), rv.data)
