import abc
import typing as t
from datetime import datetime
from kavallerie.request import User, Request


class Source(abc.ABC):

    @property
    @abc.abstractmethod
    def create_schema(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def update_schema(self) -> dict:
        pass

    @abc.abstractmethod
    def find(self,
             credentials: t.Dict, request: Request) -> t.Optional[User]:
        pass

    @abc.abstractmethod
    def fetch(self, uid: t.Any, request: Request) -> t.Optional[User]:
        pass

    @abc.abstractmethod
    def delete(self,  uid: t.Any, request: Request) -> bool:
        pass

    @abc.abstractmethod
    def update(self,  uid: t.Any, data: dict, request: Request) -> bool:
        pass

    @abc.abstractmethod
    def add(self, data: dict, request: Request):
        pass


class Authenticator:

    user_key: str
    sources: t.Iterable[Source]

    def __init__(self, user_key: str, sources: t.Iterable[Source]):
        self.sources = sources
        self.user_key = user_key

    def from_credentials(self,
                         request, credentials: dict) -> t.Optional[User]:
        for source in self.sources:
            user = source.find(credentials, request)
            if user is not None:
                return user

    def identify(self, request) -> t.Optional[User]:
        if request.user is not None:
            return request.user

        if (session := request.utilities.get('http_session')) is not None:
            if (userid := session.get(self.user_key, None)) is not None:
                for source in self.sources:
                    user = source.fetch(userid, request)
                    if user is not None:
                        request.user = user
                        return user

    def forget(self, request) -> t.NoReturn:
        if (session := request.utilities.get('http_session')) is not None:
            session.clear()
        request.user = None

    def remember(self, request, user: User) -> t.NoReturn:
        if (session := request.utilities.get('http_session')) is not None:
            session[self.user_key] = user.id
        request.user = user
