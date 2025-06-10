import abc
import typing as t
from datetime import datetime
from kavallerie.meta import User, Request


class Source(abc.ABC):

    @abc.abstractmethod
    def find(self,
             credentials: t.Dict, request: Request) -> t.Optional[User]:
        pass

    @abc.abstractmethod
    def fetch(self, uid: t.Any, request: Request) -> t.Optional[User]:
        pass


class AuthenticationWrapper:

    def __init__(self, user: User, request: Request):
        self.user = user
        self.request = request


class Authenticator:

    user_key: str
    sources: t.Iterable[Source]

    def __init__(self, sources: t.Iterable[Source], user_key: str = "user"):
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
