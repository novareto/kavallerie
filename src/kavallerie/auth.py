import abc
import typing as t
import logging
from datetime import datetime
from kavallerie.meta import User, Request


logger = logging.getLogger(__name__)


class Source(abc.ABC):

    @abc.abstractmethod
    def find(self,
             credentials: t.Dict, request: Request) -> User | None:
        pass

    @abc.abstractmethod
    def fetch(self, uid: t.Any, request: Request) -> User | None:
        pass


Preflight = t.Callable[[Request], User | None]


class BaseAuthenticator:

    sources: list[Source]
    preflights: list[Preflight]

    def __init__(self,
                 sources: t.Iterable[Source] | None = None,
                 preflights: t.Iterable[Preflight] | None = None
                 ):
        self.sources = sources is not None and list(sources) or []
        self.preflights = preflights is not None and list(preflights) or []

    def from_credentials(self,
                         request, credentials: dict) -> User | None:
        for source in self.sources:
            user = source.find(credentials, request)
            if user is not None:
                return user

    def identify(self, request) -> User | None:
        if request.user is not None:
            logger.info(f'Request contains a user: {request.user}. '
                        'Skipping authentication.')
            return request.user

        if self.preflights:
            logger.info(f'Authentication preflight found.')
            for resolver in self.preflights:
                if (user := resolver(request)) is not None:
                    logger.info(
                        f'Preflight user found by {resolver}: {user}.')
                    request.user = user
                    return user
            logger.info(f'Authentication preflight unsuccessful.')

        logger.info(f'Authentication initiated.')
        if (userid := self.get_stored_id(request)) is not None:
            for source in self.sources:
                user = source.fetch(userid, request)
                if user is not None:
                    logger.info(
                        f'Authentication by {source} successful: {user}')
                    request.user = user
                    return user

    def get_stored_id(self, request):
        pass

    def forget(self, request) -> None:
        pass

    def remember(self, request, user: User) -> None:
        pass


class HTTPSessionAuthenticator(BaseAuthenticator):

    user_key: str

    def __init__(self, user_key: str = "user", **kwargs):
        self.user_key = user_key
        super().__init__(**kwargs)

    def get_stored_id(self, request):
        if (session := request.utilities.get('http_session')) is not None:
            return session.get(self.user_key, None)

    def forget(self, request) -> None:
        if (session := request.utilities.get('http_session')) is not None:
            session.clear()
        request.user = None

    def remember(self, request, user: User) -> None:
        if (session := request.utilities.get('http_session')) is not None:
            session[self.user_key] = user.id
        request.user = user
