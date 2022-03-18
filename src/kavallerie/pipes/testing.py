import typing as t
import http_session
from kavallerie.pipes.authentication import Source
from kavallerie.request import Request, User


class DictSource(Source):

    def __init__(self, users: t.Mapping[str, str]):
        self.users = users

    def find(self, credentials: t.Dict, request: Request) -> t.Optional[User]:
        username = credentials.get('username')
        password = credentials.get('password')
        if username is not None and username in self.users:
            if self.users[username] == password:
                user = User()
                user.id = username
                return user

    def fetch(self, uid, request) -> t.Optional[User]:
        if uid in self.users:
            user = User()
            user.id = uid
            return user


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
