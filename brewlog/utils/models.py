from math import ceil


class DefaultModelMixin(object):

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):  # pragma: no cover
        return unicode(self).encode('utf-8')


class Pagination(object):  # pragma: no cover

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
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def paginate(query, page_num, per_page):
    return query.offset(page_num * per_page).limit(per_page).all()


def get_page(request, arg_name='p'):
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1
