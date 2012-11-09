# -*- coding: utf-8 -*-

__revision__ = '$Id$'

import wtforms as wf

from forms.base import BaseForm
from models.base import BrewerProfile


class ProfileForm(BaseForm):
    first_name = wf.TextField('first name')
    last_name = wf.TextField('last name')
    nick = wf.TextField('nick')
    email = wf.TextField('email')
    location = wf.TextField('location')
    about_me = wf.TextAreaField('about me')

    def save(self, user, obj=None):
        if obj is None:
            obj = BrewerProfile(parent=user.key, user=user.key,
                first_name=self.first_name.data,
                last_name=self.last_name.data,
                nick=self.nick.data,
                email=self.email.data,
                location=self.location.data,
                about_me=self.about_me.data,
            )
        return super(ProfileForm, self).save(user, obj, save=True)
