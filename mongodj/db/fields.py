from django.db import models
from django.db.models import Field
from django.utils.translation import ugettext_lazy as _

__all__ = ["ListField", ]

class ListField(Field):
    """A list field that wraps a standard field, allowing multiple instances
    of the field to be used as a list in the database.
    """

    default_error_messages = {
        'invalid': _(u'This value must be an string.'),
    }

    description = _("List Field")
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        if 'default' not in kwargs:
            kwargs['default'] = []
        Field.__init__(self, *args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if hasattr(value, "__iter__"):
            return list(value)
        #???
        return value

    def to_python(self, value):
        if value is None:
            return []
        return value

    def get_default(self):
        "Returns the default value for this field."
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return []
    