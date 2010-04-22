from django.db import models
from django.utils.translation import ugettext_lazy as _
from mongodj.fields import ListField, SortedListField, DictField
from mongodj.fields import SetListField, EmbeddedModel


class Blog(models.Model):

    title = models.CharField(max_length=200)

    class Meta:
        capped = True
        collection_max = 25
    
    def __unicode__(self):
        return "Blog: %s" % self.title

class Entry(models.Model):

    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)
    date_published = models.DateTimeField()
    blog = models.ForeignKey(Blog, null=True, blank=True)
    afile = models.FileField(upload_to='whatever', blank=True)

    def has_file_content(self):
        if self.afile and self.afile.read() is not None:
            return "There is a file"
        return "File empty"
    
    def __unicode__(self):
        return "Entry: %s" % (self.title)

class Person(models.Model):
    
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    age = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return u"Person: %s %s" % (self.name, self.surname)


class StandardAutoFieldModel(models.Model):

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
