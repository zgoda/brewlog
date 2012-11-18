# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from webapp2_extras.i18n import lazy_gettext as _

from handlers.base import BaseRequestHandler

from forms.brew import BrewForm


class BrewHandler(BaseRequestHandler):

    def add_brew(self):
        form = BrewForm(self.request.POST)
        if self.request.POST:
            if form.validate():
                brew = form.save()
                self.session.add_flash(_('brew %s saved') % brew.name)
                next = self.uri_for('brew-details', keyid=brew.key.urlsafe())
                return self.redirect(next)
        ctx = {
            'form': form,
        }
        self.render('brewery/brew_form.html', ctx)
