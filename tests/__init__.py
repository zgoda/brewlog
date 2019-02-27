import os


class BrewlogTests:

    TEMPLATES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'brewlog/templates',
    )

    def login(self, email):
        return self.client.get('/auth/local?email=%s' % email, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
