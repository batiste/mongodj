from django.db import models
from django.db.models import Field
from django.utils.translation import ugettext_lazy as _

__all__ = ["ListField", ]

class ListField(Field):
    """A list field that wraps a standard field, allowing multiple instances
    of the field to be used as a list in the database.
    """

    default_error_messages = {
        'invalid': _(u'This value must be a list or an iterable.'),
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

class SortedListField(ListField):
    """A ListField that sorts the contents of its list before writing to
    the database in order to ensure that a sorted list is always
    retrieved.
    """

    description = _("Sorted Field")
    _ordering = None

    def __init__(self, *args, **kwargs):
        if 'ordering' in kwargs.keys():
            self._ordering = kwargs.pop('ordering')
        super(SortedListField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, list):
            if hasattr(value, "__iter__"):
                value = list(value)
        if self._ordering is not None:
            return sorted(value, key=itemgetter(self._ordering))
        return sorted(value)

class DictField(Field):
    """A dictionary field that wraps a standard Python dictionary.
    Key cannot contains . or $ for query problems.
    """
    description = _("Dict Field")

    default_error_messages = {
        'invalid': _(u'This value must be a dictionary.'),
        'invalid_key': _(u'Invalid dictionary key name - Keys cannot contains . or $ for query problems'),
    }

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. 
        """
        if not isinstance(value, dict):
            raise exceptions.ValidationError(self.error_messages['invalid'])

        if any(('.' in k or '$' in k) for k in value):
            raise exceptions.ValidationError(self.error_messages['invalid_key'])

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def get_default(self):
        "Returns the default value for this field."
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return {}
