import collections

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
        if hasattr(self, 'absolute_url') and not 'absolute_url' in fields:
            fields.add('absolute_url')
        fields = list(fields)
        return self.data(fields)

    def full_data(self):
        fields = [k for k in self.__dict__.keys() if not k.startswith('_')]
        if hasattr(self, 'absolute_url'):
            fields.append('absolute_url')
        return self.data(fields)

