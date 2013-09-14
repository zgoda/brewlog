from ll import sisyphus

from brewlog import config
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

    def _find_oldest_file(self):
        dirname = os.path.join(config.UPLOAD_DIR, 'import')
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        try:
            return sorted_directory_listing(dirname)[0]
        except:
            return None

    def _get_brewery_for_file(self, fn):
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
