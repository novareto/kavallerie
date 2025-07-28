import typing as t
from kavallerie.auth import Source
from kavallerie.schema import JSONSchema
from kavallerie.meta import Request, User


class DictSource(Source):

    create_schema = JSONSchema({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "User",
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "User name."
            },
            "password": {
                "type": "string",
                "description": "User password"
            }
        },
        "required": ["username", "password"],
    })

    update_schema = JSONSchema({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "User update",
        "type": "object",
        "properties": {
            "password": {
                "type": "string",
                "description": "User password"
            }
        },
        "required": ["password"],
    })

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

    def delete(self,  uid: t.Any, request: Request) -> bool:
        if uid not in self.users:
            return False

        del self.users[uid]
        return True

    def update(self,  uid: t.Any, data: dict, request: Request) -> bool:
        if uid not in self.users:
            return False

        errors = tuple(self.update_schema.validate(data))
        if not errors:
            self.users[uid] = data['password']
        return False

    def add(self, data: dict, request: Request):
        errors = tuple(self.update_schema.validate(data))
        if not errors:
            if data['username'] in self.users:
                return False
            self.users[data['username']] = data['password']
        return False
