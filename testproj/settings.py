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


INSTALLED_APPS = (
    "testproj.myapp",
)