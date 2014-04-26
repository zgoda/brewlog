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

    class user3:
        email = 'user3@example.com'
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


class CustomExportTemplateData(DataSet):

    class export1:
        user = BrewerProfileData.user1
        name = 'custom #1'

    class export2:
        user = BrewerProfileData.user2
        name = 'custom #2'


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


class FermentationStepData(DataSet):

    class fstep1:
        brew = BrewData.brew1
        name = 'primary'
        date = datetime.datetime.utcnow()
        og = 12.5
        volume = 21


class TastingNoteData(DataSet):

    class note1:
        brew = BrewData.brew1
        author = BrewerProfileData.user0
        date = datetime.date(2013, 9, 20)
        text = 'nice brew'

    class note2:
        brew = BrewData.brew2
        author = BrewerProfileData.user0
        date = datetime.date(2013, 9, 21)
        text = 'ugly'

    class note3:
        brew = BrewData.hidden1
        author = BrewerProfileData.user0
        date = datetime.date(2013, 9, 22)
        text = 'infected'
