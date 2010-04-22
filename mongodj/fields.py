from django.db import models
from django.db.models import Field
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from pymongo.objectid import ObjectId
from django.db.models import signals
from django.db.models.fields import AutoField as DJAutoField

__all__ = ["ListField", "DictField", "SetListField", "SortedListField", "EmbeddedModel"]

class EmbeddedModel(models.Model):
    _embedded_in =None
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pk = ObjectId()
        if self._embedded_in  is None:
            raise RuntimeError("Invalid save")
        self._embedded_in.save()

    def serialize(self):
        if self.pk is None:
            self.pk = ObjectId()
        result = {'_app':self._meta.app_label, 
            '_model':self._meta.module_name,
            '_id':self.pk}
        for field in self._meta.fields:
            result[field.attname] = getattr(self, field.attname)
        return result
    
class ListField(Field):
    """A list field that wraps a standard field, allowing multiple instances
    of the field to be used as a list in the database.
    """

    default_error_messages = {
        'invalid': _(u'This value must be a list or an iterable.'),
        'invalid_value': _(u'Invalid value in list.'),
    }

    description = _("List Field")
    _internaltype = None
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        if 'default' not in kwargs:
            kwargs['default'] = []
        if 'type' in kwargs:
            self._internaltype = kwargs.pop("type")
            
        Field.__init__(self, *args, **kwargs)

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. 
        """
        if not isinstance(value, list) and (not hasattr(value, "__iter__")):
            raise exceptions.ValidationError(self.error_messages['invalid'])

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])
        if self._internaltype is not None:
            for v in value:
                if not isinstance(v, self._internaltype):
                    raise exceptions.ValidationError(self.error_messages['invalid_value'])
        
    def get_prep_value(self, value):
        if value is None:
            return None
        return list(value)

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
        if 'type' in kwargs:
            self._internaltype = kwargs.pop("type")
        super(SortedListField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, list) and (not hasattr(value, "__iter__")):
            raise exceptions.ValidationError(self.error_messages['invalid'])
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
    _internaltype = None
    default_error_messages = {
        'invalid': _(u'This value must be a set.'),
        'invalid_value': _(u'Invalid value in list.'),
    }

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        if 'default' not in kwargs:
            kwargs['default'] = set()
        if 'type' in kwargs:
            self._internaltype = kwargs.pop("type")

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
        if self._internaltype is not None:
            for v in value:
                if not isinstance(v, self._internaltype):
                    raise exceptions.ValidationError(self.error_messages['invalid_value'])

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

#
# Fix standard models to work with mongodb
#

def autofield_to_python(value):
    if value is None:
        return value
    try:
        return str(value)
    except (TypeError, ValueError):
        raise exceptions.ValidationError(self.error_messages['invalid'])

def autofield_get_prep_value(value):
    if value is None:
        return None
    return ObjectId(value)

def fix_autofield(sender, **kwargs):
    """
    Fix autofield
    """
    cls = sender
    if isinstance(cls._meta.pk, DJAutoField):
        pk = cls._meta.pk
        setattr(pk, "to_python", autofield_to_python)
        setattr(pk, "get_prep_value", autofield_get_prep_value)
            

signals.class_prepared.connect(fix_autofield)    