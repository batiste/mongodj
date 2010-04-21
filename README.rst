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

Features:

	- multidb (use a mixin of SQL and NotSQL DB)
	- Embdedded model management
	- SQL model management
	- Routing on mongodb of some apps

Extra fields:

	- Dictionary Field
	- List Field
	- Sorted List Field	

TODO (ramdom order):

	- south support
	- gridfs
	- geofield
	- set field
	- special manager for complex query (map/reduce)


Settings configuration
----------------------

Set up database with Rel and not rel database.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',                     
        'USER': '',                     
        'PASSWORD': '',                  
        'HOST': '',                     
        'PORT': '',                     
    },
    'mongodb': {
        'ENGINE': 'mongodj.db',
        'NAME': 'test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
        'SUPPORTS_TRANSACTIONS': False,
    },
}

in INSTALLED_APPS 'django.contrib.contenttypes' is required.

Activate routing adding::

	DATABASE_ROUTERS = ['mongodj.db.router.MongoDBRouter']


Select apps that you want manage in mongodb::

	MONGODB_MANAGED_APPS = ['testproj.myapp', ]


Extra
-----

Hey dudes add an issue if you want some other features!

Examples::

    Blog.objects.count()
    Blog.objects.get(title="my title")
    Blog.objects.filter(title="my title")
    Entry.objects.order_by('-date_published')
    Entry.objects.filter(date_published__lt=now)
    entry1 = Entry(title="entry 1", blog=blog1)
    Entry.objects.filter(blog=blog1.pk)	

PS: for extra examples and usage look the testproj (models.py and test.py).