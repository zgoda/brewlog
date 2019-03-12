class BrewlogTests:

    def login(self, email):
        return self.client.get(f'/auth/local?email={email}', follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
