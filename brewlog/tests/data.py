import datetime

from fixture import DataSet


class BrewerProfileData(DataSet):
    class user0:
        email = 'user@example.com'
        nick = 'example user'
        created = datetime.datetime.now()
    class user1:
        email = 'user1@example.com'
        nick = 'example user #1'
        created = datetime.datetime.now()
    class user2:
        email = 'user2@example.com'
        nick = 'example user #2'
        created = datetime.datetime.now()


class BreweryData(DataSet):
    class brewery1:
        name = 'brewery #1'
        brewer = BrewerProfileData.user1
        created = datetime.datetime.now()
    class brewery2:
        name = 'brewery #2'
        brewer = BrewerProfileData.user2
        created = datetime.datetime.now()


class BrewData(DataSet):
    class brew1:
        brewery = BreweryData.brewery1
        name = 'pale ale'
        code = '1'
        created = datetime.datetime.now()
