import typing as t
from kavallerie.auth import Source
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
