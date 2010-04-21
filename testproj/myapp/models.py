from django.db import models
from django.utils.translation import ugettext_lazy as _
from mongodj.db.fields import ListField, SortedListField, DictField, SetListField

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
    _id = StringAutoField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Blog: %s" % self.title


class Entry(models.Model):
    _id = StringAutoField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)
    date_published = models.DateTimeField()
    blog = StringForeignKey(Blog, null=True, blank=True)
    
    def __unicode__(self):
        return "Entry: %s" % (self.title)

class Person(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    age = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return u"Person: %s %s" % (self.name, self.surname)


class StandardAutoFieldModel(models.Model):
    _id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Standard model: %s" % (self.title)

class TestFieldModel(models.Model):
    title = models.CharField(max_length=200)
    mlist = ListField()
    mlist_default = ListField(default=["a", "b"])
    slist = SortedListField()
    slist_default = SortedListField(default=["b", "a"])
    mdict = DictField()
    mdict_default = DictField(default={"a": "a", 'b':1})
    mset = SetListField()
    mset_default = SetListField(default=set(["a", 'b']))

    def __unicode__(self):
        return "Test special field model: %s" % (self.title)