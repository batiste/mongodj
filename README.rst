mongoDJ
-------

MongoDB backend for Django.

The aim of the project is to create a native django DB backend
for mongo (so that it can be accessed through the django ORM).

The project is in the early stage

mongoDB is accessed through pyMongo and relies on django-trunk (>=1.2)

Features that works::

    Blog.objects.count()
    Blog.objects.get(title="my title")
    Blog.objects.filter(title="my title")
    Entry.objects.order_by('-date_published')
    Entry.objects.filter(date_published__lt=now)
    entry1 = Entry(title="entry 1", blog=blog1)
    Entry.objects.filter(blog=blog1.pk)