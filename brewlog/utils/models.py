import collections
from math import ceil

from flask import abort


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def paginate(query, page_num, per_page):
    return query.offset(page_num*per_page).limit(per_page).all()


def get_or_404(cls, pk):
    obj = cls.query.get(pk)
    if obj is None:
        abort(404)
    return obj


class DataModelMixin(object):

    def data(self, fields):
        Data = collections.namedtuple('Data', fields)
        kw = {}
        for fn in fields:
            kw[fn] = getattr(self, fn)
        return Data(**kw)

    def summary_data(self, fields=None):
        if fields is None:
            fields = []
        fields = set(fields)
        fields.add('id')
        if hasattr(self, 'absolute_url'):
            fields.add('absolute_url')
        fields = list(fields)
        return self.data(fields)

    def full_data(self):
        fields = [k for k in self.__dict__.keys() if not k.startswith('_')]
        if hasattr(self, 'absolute_url'):
            fields.append('absolute_url')
        return self.data(fields)
