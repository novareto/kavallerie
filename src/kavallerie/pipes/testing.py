import http_session


class MemorySessionStore(http_session.Store):

    def __init__(self):
        self._store = {}

    def touch(self, sid):
        pass

    def get(self, sid):
        """We return a copy, to avoid mutability by reference."""
        from copy import deepcopy

        data = self._store.get(sid)
        if data is not None:
            return deepcopy(data)
        return data

    def set(self, sid, session):
        self._store[sid] = session

    def clear(self, sid):
        if sid in self._store:
            self._store[sid].clear()

    def delete(self, sid):
        del self._store[sid]
