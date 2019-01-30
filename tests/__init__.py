class BrewlogTests:

    def login(self, client, email=None):
        if email is None:
            email = 'user@example.com'
        return client.get('/auth/local?email=%s' % email, follow_redirects=True)

    def logout(self, client):
        return client.get('/auth/logout', follow_redirects=True)
