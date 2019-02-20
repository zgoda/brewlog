class BrewlogTests:

    def login(self, email):
        return self.client.get('/auth/local?email=%s' % email, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
