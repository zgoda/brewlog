import datetime

from fixture import DataSet


class BrewerProfileData(DataSet):
    class user0:
        email = 'user@example.com'
        nick = 'example user'
        created = datetime.datetime.utcnow()
    class user1:
        email = 'user1@example.com'
        nick = 'example user #1'
        created = datetime.datetime.utcnow()
    class user2:
        email = 'user2@example.com'
        nick = 'example user #2'
        created = datetime.datetime.utcnow()
    class hidden0:
        email = 'hidden0@example.com'
        nick = 'hidden user'
        created = datetime.datetime.utcnow()
        is_public = False
    class hidden1:
        email = 'hidden1@example.com'
        nick = 'hidden user #1'
        created = datetime.datetime.utcnow()
        is_public = False


class CustomLabelTemplateData(DataSet):
    class design1:
        user = BrewerProfileData.user1
        name = 'custom #1'
        text = '#### {{ brew.name }}'


class BreweryData(DataSet):
    class brewery1:
        name = 'brewery #1'
        brewer = BrewerProfileData.user1
        created = datetime.datetime.utcnow()
    class brewery2:
        name = 'brewery #2'
        brewer = BrewerProfileData.user2
        created = datetime.datetime.utcnow()
    class hidden1:
        name = 'hidden brewery #1'
        brewer = BrewerProfileData.hidden0
        created = datetime.datetime.utcnow()


class BrewData(DataSet):
    class brew1:
        brewery = BreweryData.brewery1
        name = 'pale ale'
        code = '1'
        created = datetime.datetime.utcnow()
    class brew2:
        brewery = BreweryData.brewery1
        name = 'hidden czech pilsener'
        code = '2'
        created = datetime.datetime.utcnow()
        is_public = False
    class hidden1:
        brewery = BreweryData.hidden1
        name = 'hidden amber ale'
        code = '1'
        created = datetime.datetime.utcnow()
