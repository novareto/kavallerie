import abc
import typing as t
import logging
from wrapt import ObjectProxy
from datetime import datetime
from kavallerie.meta import User, Request
from types import MappingProxyType


logger = logging.getLogger(__name__)



class AuthenticationInfo(t.TypedDict):
    source_id: str
    user_id: str


class Source(abc.ABC):

    title: str
    description: str

    @property
    @abc.abstractmethod
    def create_schema(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def update_schema(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def search_schema(self) -> dict:
        pass

    @abc.abstractmethod
    def count(self, criterions: dict) -> int:
        pass

    @abc.abstractmethod
    def search(self, criterions: dict, index: int = 0, size: int = 10) -> t.Iterator[User]:
        pass

    @abc.abstractmethod
    def find(self,
             credentials: t.Dict, request: Request) -> User | None:
        pass

    @abc.abstractmethod
    def fetch(self, uid: t.Any, request: Request) -> User | None:
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

    @abc.abstractmethod
    def __iter__(self) -> t.Iterator[User]:
        pass


class SourceProxy(ObjectProxy):
    id: str

    def __init__(self, source: Source, sid: str):
        super().__init__(source)
        self.id = sid


class Sources(t.Iterable[Source]):

    _sources: t.Mapping[str, SourceProxy]

    def __init__(self, sources: t.Mapping[str, Source]):
        self._sources = MappingProxyType({
            sid: SourceProxy(source, sid) for sid, source in sources.items()
        })

    def __getitem__(self, name: str):
        return self._sources.__getitem__(name)

    def __iter__(self):
        yield from self._sources.values()

    def items(self):
        return self._sources.items()

    def keys(self):
        return self._sources.keys()

    def __contains__(self, name: str):
        return name in self._sources


Preflight = t.Callable[[Request], User | None]


class BaseAuthenticator:

    sources: dict[str, Source]
    preflights: list[Preflight]

    def __init__(self,
                 sources: t.Mapping[str, Source] | None = None,
                 preflights: t.Iterable[Preflight] | None = None
                 ):
        self.sources = sources is not None and sources or {}
        self.preflights = preflights is not None and list(preflights) or []

    def from_credentials(self,
                         request,
                         credentials: dict) -> tuple[str, User] | None:
        for source_id, source in self.sources.items():
            user = source.find(credentials, request)
            if user is not None:
                return source_id, user

    def identify(self, request) -> User | None:
        if self.preflights:
            logger.info(f'Authentication preflight found.')
            for resolver in self.preflights:
                if (user := resolver(request)) is not None:
                    logger.info(
                        f'Preflight user found by {resolver}: {user}.')
                    return user
            logger.info(f'Authentication preflight unsuccessful.')

        logger.info(f'Authentication initiated.')
        if (info := self.get_stored_info(request)) is not None:
            source = self.sources[info['source_id']]
            user = source.fetch(info['user_id'], request)
            if user is not None:
                logger.info(
                    f"Authentication by {info['source_id']} successful: {user}")
                return user

    def get_stored_info(self, request) -> AuthenticationInfo:
        pass

    def forget(self, request) -> None:
        pass

    def remember(self, request, source_id: str, user: User) -> None:
        pass


class HTTPSessionAuthenticator(BaseAuthenticator):

    user_key: str

    def __init__(self, user_key: str = "user", **kwargs):
        self.user_key = user_key
        super().__init__(**kwargs)

    def get_stored_info(self, request) -> AuthenticationInfo:
        if (session := request.utilities.get('http_session')) is not None:
            return session.get(self.user_key, None)

    def forget(self, request) -> None:
        if (session := request.utilities.get('http_session')) is not None:
            session.clear()
        request.user = None

    def remember(self, request, source_id: str, user: User) -> None:
        if (session := request.utilities.get('http_session')) is not None:
            session[self.user_key] = AuthenticationInfo(
                user_id=user.id,
                source_id=source_id
            )
        request.user = user
