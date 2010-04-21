from django.db import models
from django.utils.translation import ugettext_lazy as _
from mongodj.db.fields import ListField, SortedListField, DictField
from mongodj.db.fields import SetListField, EmbeddedModel, StringAutoField
from mongodj.db.fields import StringForeignKey


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
    afile = models.FileField(upload_to='whatever')
    
    def __unicode__(self):
        return "Entry: %s" % (self.title)

class Person(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    age = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return u"Person: %s %s" % (self.name, self.surname)


class StandardAutoFieldModel(models.Model):
    primary = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Standard model: %s" % (self.title)

class EModel(EmbeddedModel):
    title = models.CharField(max_length=200)
    pos = models.IntegerField(default = 10)

    def test_func(self):
        return self.pos

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