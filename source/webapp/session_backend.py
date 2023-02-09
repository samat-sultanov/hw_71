from django.contrib.sessions.backends.db import SessionStore as DbSessionStore
from webapp.models import Cart


class SessionStore(DbSessionStore):
    def cycle_key(self):
        data = self._session
        key = self.session_key
        self.create()
        self._session_cache = data
        if key:
            Cart.objects.filter(user_session=key).update(user_session=self.session_key)
            self.delete(key)
