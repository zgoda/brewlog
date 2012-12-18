# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from webapp2_extras.i18n import lazy_gettext as _

from handlers.base import BaseRequestHandler
from forms.brew import BrewForm
from models.simple import Batch


class BrewHandler(BaseRequestHandler):

    def brew_list(self):
        brews = Batch.query(Batch.is_public==True).order(-Batch.created_at).fetch(10)
        ctx = {
            'brews': brews
        }
        self.render('brewery/brew_list.html', ctx)

    def add_brew(self):
        form = BrewForm(self.request.POST)
        if self.request.POST:
            if form.validate():
                brew = form.save(user=self.current_user)
                self.session.add_flash(_('brew %s saved') % brew.name)
                next = self.uri_for('brew-details', keyid=brew.key.urlsafe())
                return self.redirect(next)
        ctx = {
            'form': form,
        }
        self.render('brewery/brew_form.html', ctx)
