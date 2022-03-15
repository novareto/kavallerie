import abc
import typing as t
from kavallerie.response import Response
from kavallerie.request import Request, User
from kavallerie.pipeline import Handler, MiddlewareFactory


Filter = t.Callable[[Handler, Request], t.Optional[Response]]


class Source(abc.ABC):

    @abc.abstractmethod
    def find(self,
             credentials: t.Dict, request: Request) -> t.Optional[User]:
        pass

    @abc.abstractmethod
    def fetch(self, uid: t.Any, request: Request) -> t.Optional[User]:
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


class Authentication(MiddlewareFactory):

    class Configuration(t.NamedTuple):
        sources: t.Iterable[Source]
        user_key: str = 'user'
        filters: t.Optional[t.Iterable[Filter]] = None

    def __post_init__(self):
        self.authenticator = Authenticator(
            self.config.user_key,
            self.config.sources
        )

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def authentication_middleware(request):
            request.utilities['authentication'] = self.authenticator
            _ = self.authenticator.identify(request)
            if self.config.filters:
                for filter in self.config.filters:
                    if (resp := filter(handler, request)) is not None:
                        del request.utilities['authentication']
                        return resp

            response = handler(request)
            del request.utilities['authentication']
            return response

        return authentication_middleware
