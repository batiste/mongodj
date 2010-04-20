
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'mongodj.db',
        'NAME': 'test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
        'SUPPORTS_TRANSACTIONS': False,
    },
}

ROOT_URLCONF = 'testproj.urls'

INSTALLED_APPS = (
    "testproj.myapp",
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.admin',
)

#MIDDLEWARE_CLASSES = (
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.common.CommonMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.doc.XViewMiddleware',
#)

SECRET_KEY = "XaalaLDkS029123Jk"