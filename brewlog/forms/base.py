from flask_wtf import Form


class BaseForm(Form):

    def save(self, obj, save=False):
        self.populate_obj(obj)
        if save:
            obj.save()
        return obj
