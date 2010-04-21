from django.db import models
from django.db.models import Field
from django.utils.translation import ugettext_lazy as _

__all__ = ["ListField", "DictField", "SetListField", "SortedListField"]

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


class SetListField(Field):
    """A list field that allows only one instance for item.
    """

    description = _("List Set Field")
    
    default_error_messages = {
        'invalid': _(u'This value must be a set.'),
    }

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        if 'default' not in kwargs:
            kwargs['default'] = set()
        Field.__init__(self, *args, **kwargs)
    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. 
        """
        if not isinstance(value, set):
            raise exceptions.ValidationError(self.error_messages['invalid'])

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
        return set()


    def get_db_prep_value(self, value, connection, prepared=False):
        """Returns field's value prepared for interacting with the database
        backend.

        Used by the default implementations of ``get_db_prep_save``and
        `get_db_prep_lookup```
        """
        if not prepared:
            value = list(self.get_prep_value(value))
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, set):
            if hasattr(value, "__iter__"):
                value = set(value)
        return set(value)
    
    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value.
        """
        if value is None:
            return set()
        return set(value)
