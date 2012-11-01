# -*- coding: utf-8 -*-

__revision__ = '$Id$'


import simpleauth

import secrets
from handlers.base import BaseRequestHandler


class ProfileHandler(BaseRequestHandler):

    def get(self):
        self.render('account/profile.html', {
            'user': self.current_user,
            'session': self.auth.get_user_by_session(),
        })


class AuthHandler(BaseRequestHandler, simpleauth.SimpleAuthHandler):

    OAUTH2_CSRF_STATE = True

    USER_ATTRS = {
        'facebook' : {
            'id'     : lambda id: ('avatar_url', 'http://graph.facebook.com/{0}/picture?type=large'.format(id)),
            'name'   : 'name',
            'link'   : 'link'
        },
        'google'   : {
            'picture': 'avatar_url',
            'name'   : 'name',
            'link'   : 'link'
        },
        'windows_live': {
            'avatar_url': 'avatar_url',
            'name'      : 'name',
            'link'      : 'link'
        },
        'twitter'  : {
            'profile_image_url': 'avatar_url',
            'screen_name'      : 'name',
            'link'             : 'link'
        },
        'linkedin' : {
            'picture-url'       : 'avatar_url',
            'first-name'        : 'name',
            'public-profile-url': 'link'
        },
        'openid'   : {
            'id'      : lambda id: ('avatar_url', '/img/missing-avatar.png'),
            'nickname': 'name',
            'email'   : 'link'
        }
    }

    def _on_signin(self, data, auth_info, provider):
        auth_id = '%s:%s' % (provider, data['id'])
        user_obj = self.auth.store.user_model.get_by_auth_id(auth_id)
        _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])
        if user_obj:
            user_obj.populate(**_attrs)
            user_obj.put()
            self.auth.set_session(self.auth.store.user_to_dict(user_obj))
        else:
            if self.logged_in:
                u = self.current_user
                u.populate(**_attrs)
                success, info = u.add_auth_id(auth_id)
            else:
                ok, user_obj = self.auth.store.user_model.create_user(auth_id, **_attrs)
                if ok:
                    self.auth.set_session(self.auth.store.user_to_dict(user_obj))
        self.redirect('/profile')

    def logout(self):
        self.auth.unset_session()
        self.redirect('/')

    def _to_user_model_attrs(self, data, attrs_map):
        """Get the needed information from the provider dataset."""
        user_attrs = {}
        for k, v in attrs_map.iteritems():
            attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
            user_attrs.setdefault(*attr)
        return user_attrs

    def _callback_uri_for(self, provider):
        return self.uri_for('auth-callback', provider=provider, _full=True)

    def _get_consumer_info_for(self, provider):
        return secrets.AUTH_CONFIG[provider]
