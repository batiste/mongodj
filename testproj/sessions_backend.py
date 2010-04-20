from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore as SS
from pymongo.objectid import ObjectId

class SessionStore(SS):

    def _get_new_session_key(self):
        "Returns session key that isn't being used."
        return str(ObjectId())