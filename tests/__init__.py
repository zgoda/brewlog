# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


class BrewlogTests:

    def login(self, email):
        return self.client.get(f'/auth/local?email={email}', follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
