import uuid
import typing as t
from kavallerie.auth import Source
from kavallerie.schema import JSONSchema
from kavallerie.meta import Request, User


class DictUser(User):

    def __init__(self, id: str | int | uuid.UUID):
        self.id = id


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

    search_schema = JSONSchema({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "User search",
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Username"
            }
        }
    })

    def __init__(self,
                 users: t.Mapping[str, str], *,
                 title: str,
                 description: str):
        self.users = users
        self.title = title
        self.description = description

    def __iter__(self):
        for username in self.users.keys():
            yield DictUser(username)

    def find(self, credentials: t.Dict, request: Request) -> User | None:
        username = credentials.get('username')
        password = credentials.get('password')
        if username is not None and username in self.users:
            if self.users[username] == password:
                return DictUser(username)

    def fetch(self, uid, request) -> User | None:
        if uid in self.users:
            return DictUser(uid)

    def delete(self,  uid: t.Any, request: Request) -> bool:
        if uid not in self.users:
            return False

        del self.users[uid]
        return True

    def count(self, data):
        if not data:
            return len(self.users)

        found = 0
        for i in self.users:
            if data['username'] in i:
                found += 1
        return found

    def search(self, data, index: int = 0, limit: int = 10):
        if not data:
            users = [DictUser(i) for i in self.users]
        else:
            users = [DictUser(i) for i in self.users if data['username'] in i]
        return users[index:index+limit]

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
