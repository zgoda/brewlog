import os

from ll import sisyphus
from flask_mail import Message

from brewlog import config, mail
from brewlog.models import Brewery
from brewlog.utils.files import sorted_directory_listing


class BeerXMLProcessor(sisyphus.Job):
    projectname = 'brewlog'
    argdescription = 'process single BeerXML file from uploads directory'
    maxtime = 3600
    keepfilelogs = 30
    encoding = 'utf-8'

    def execute(self):
        fn = self._find_oldest_file()
        if fn:
            brewery = self._get_brewery_for_file(fn)
            if brewery:
                imported, failed = brewery.import_recipes_from(fn, filetype='beerxml')
                msg = u'%d recipes imported, %d failed from file %s' % (imported, failed, fn)
                self.log.info(msg)
                if imported > 0:
                    os.unlink(fn)
                with mail.connect() as connection:
                    user = brewery.brewer
                    subject = u'Your BeerXML file has been processed'
                    message = Message(recipients=[user.email], body=message, subject=subject)
                    connection.send(message)

    def _find_oldest_file(self):
        dirname = os.path.join(config.UPLOAD_DIR, 'import')
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        try:
            ctime, oldest = sorted_directory_listing(dirname)[0]
            return oldest
        except:
            return None

    def _get_brewery_for_file(self, fn):
        import ipdb; ipdb.set_trace()
        try:
            fname = os.path.split(fn)[-1]
            if not fname.startswith('bid'):
                return None
            prefix, bid, tail = fname.split('_', 2)
            return Brewery.query.get(bid)
        except IndexError:
            pass # invalid file name?!


if __name__ == '__main__':
    sisyphus.executewithargs(BeerXMLProcessor())
