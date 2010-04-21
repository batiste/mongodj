from django.db import models
from django.utils.translation import ugettext_lazy as _

class StringAutoField(models.AutoField):

    default_error_messages = {
        'invalid': _(u'This value must be an string.'),
    }

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return str(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(self.error_messages['invalid'])

class StringForeignKey(models.ForeignKey):

    default_error_messages = {
        'invalid': _(u'This value must be an string.'),
    }

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(value)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return str(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(self.error_messages['invalid'])

    def db_type(self, connection):
        return unicode


class Blog(models.Model):
    primary = StringAutoField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Blog: %s" % self.title


class Entry(models.Model):
    primary = StringAutoField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)
    date_published = models.DateTimeField()
    blog = StringForeignKey(Blog, null=True, blank=True)
    
    def __unicode__(self):
        return "Entry: %s" % (self.title)


class StandardAutoFieldModel(models.Model):
    primary = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Standard model: %s" % (self.title)