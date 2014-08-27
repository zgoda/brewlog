class DefaultModelMixin(object):

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):  # pragma: no cover
        return unicode(self).encode('utf-8')


def get_page(request, arg_name='p'):
    try:
        return int(request.args.get(arg_name, '1'))
    except ValueError:
        return 1
