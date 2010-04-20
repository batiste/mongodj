mongoDJ
-------

MongoDB backend for Django.

The aim of the project is to create a native django DB backend
for mongo (so that it can be accessed through the django ORM).

This will not be a complete replacement for a django DB backend,
because MongoDB is not rel, but it will be very useful for making
mixing apps (SQL - NotSQL).

The project is in the early stage.

mongoDB is accessed through pyMongo and relies on django-trunk (>=1.2).

Some fields types are imported from mongoengine.

Features that works::

    Blog.objects.count()
    Blog.objects.get(title="my title")
    Blog.objects.filter(title="my title")
    Entry.objects.order_by('-date_published')
    Entry.objects.filter(date_published__lt=now)
    entry1 = Entry(title="entry 1", blog=blog1)
    Entry.objects.filter(blog=blog1.pk)

Extra fields:

	- Dictionary Field
	- List Field
	- Sorted List Field	

TODO (ramdom order)::

	- south support
	- gridfs
	- geofield
	- set field
	- special manager for complex query (map/reduce)

Hey dudes add an issue if you want some other features!

PS: for extra examples and usage look the testproj (models.py and test.py).