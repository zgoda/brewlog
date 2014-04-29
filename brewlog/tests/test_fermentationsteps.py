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

    def test_delete_fermentation_step_by_public(self):
        fstep_id = self.fstep.id
        url = url_for('brew-fermentationstep_delete', fstep_id=fstep_id)
        with self.app.test_client() as client:
            self.login(client, self.another_user.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_delete_fermentation_step_owner_sees_form(self):
        url = url_for('brew-fermentationstep_delete', fstep_id=self.fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

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

    def test_edit_fermentation_step_by_public(self):
        url = url_for('brew-fermentation_step', fstep_id=self.fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.another_user.email)
            data = {
                'name': 'primary (mod)',
                'date': self.fstep.date.strftime('%Y-%m-%d'),
                'og': self.fstep.og,
                'fg': self.fstep.fg,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_set_og_sets_fg(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            data = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'secondary',
                'og': 2.5,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            step = FermentationStep.query.filter_by(brew=self.brew, name=data['name']).first()
            prev_step = FermentationStep.query.filter_by(brew=self.brew).order_by(FermentationStep.date).first()
            self.assertEqual(prev_step.fg, step.og)

    def test_set_fg_changes_og(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            data_secondary = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'secondary',
                'og': 3,
                'notes': 'secondary fermentation',
            }
            rv = client.post(url, data=data_secondary, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            url = url_for('brew-fermentation_step', fstep_id=self.fstep.id)
            data_primary = {
                'name': 'primary (mod)',
                'date': self.fstep.date.strftime('%Y-%m-%d'),
                'og': self.fstep.og,
                'fg': 2,
            }
            rv = client.post(url, data=data_primary, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            next_step = FermentationStep.query.filter_by(name=data_secondary['name']).first()
            self.assertEqual(next_step.og, data_primary['fg'])

    def test_set_og_changes_fg(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            data_secondary = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'secondary',
                'og': 3,
                'notes': 'secondary fermentation',
            }
            rv = client.post(url, data=data_secondary, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(FermentationStep.query.filter_by(brew=self.brew).count(), 2)
            step = FermentationStep.query.filter_by(brew=self.brew, name=data_secondary['name']).first()
            url = url_for('brew-fermentation_step', fstep_id=step.id)
            data = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'secondary',
                'og': 2.5,
                'notes': 'secondary fermentation',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            prev_step = FermentationStep.query.filter_by(brew=self.brew).order_by(FermentationStep.date).first()
            self.assertEqual(prev_step.fg, data['og'])

    def test_insert_step_with_fg(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            data = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'pre-primary',
                'og': 12,
                'fg': 3,
                'notes': 'starter',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            step = FermentationStep.query.filter_by(name=self.fstep.name).first()
            self.assertEqual(step.og, data['fg'])

    def test_complete_fermentation_display(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            data_secondary = {
                'date': date.strftime('%Y-%m-%d'),
                'name': 'secondary',
                'og': 3,
                'fg': 2.5,
                'notes': 'secondary fermentation',
            }
            rv = client.post(url, data=data_secondary, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('5.5% ABV', rv.data)
