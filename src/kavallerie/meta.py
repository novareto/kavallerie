import abc
import uuid
import typing as t
from dataclasses import dataclass, field
from authsources.identity import User
from authsources.protocols import RequestProtocol
from horseman.response import Response
from horseman.environ import WSGIEnvironWrapper
from horseman.types import WSGICallable, HTTPMethod
from kavallerie.events import Subscribers
from kavallerie.pipeline import Pipeline


Endpoint = t.Callable[[WSGIEnvironWrapper], WSGICallable]
HTTPMethods = t.Iterable[HTTPMethod]


class APIView:
    """View with methods to act as HTTP METHOD dispatcher.
    Method names of the class must be a valid uppercase HTTP METHOD name.
    example : OPTIONS, GET, POST
    """

    def __call__(self, request: WSGIEnvironWrapper) -> Response:
        if worker := getattr(self, request.method, None):
            return worker(request)

        # Method not allowed
        return Response(405)


class RouteEndpoint(t.NamedTuple):
    method: HTTPMethod
    endpoint: Endpoint
    metadata: t.Optional[t.Dict[t.Any, t.Any]] = None

    def __call__(self, *args, **kwargs):
        return self.endpoint(*args, **kwargs)


class RouteDefinition(t.NamedTuple):
    path: str
    payload: t.Dict[HTTPMethod, RouteEndpoint]


class Route(t.NamedTuple):
    path: str
    endpoint: RouteEndpoint
    params: dict


class Request(RequestProtocol):

    __slots__ = ('app', 'user', 'utilities')

    app: t.Optional['Application']
    utilities: t.Mapping[str, t.Any]
    user: User | None
    headers: dict

    def __init__(self,
                 app: t.Optional['Application'] = None,
                 user: User | None = None,
                 headers: t.Mapping[str, t.Any] | None = None,
                 utilities: t.Mapping[str, t.Any] | None = None):
        self.app = app
        self.user = user
        self.utilities = utilities is not None and utilities or {}
        self.headers = headers is not None and headers or {}


@dataclass
class Application:
    utilities: dict = field(default_factory=dict)
    config: t.Mapping[str, t.Any] = field(default_factory=dict)
    subscribers: Subscribers = field(default_factory=Subscribers)
    request_factory: t.Callable[..., Request] = Request
    pipeline: Pipeline = field(default_factory=Pipeline)


__all__ = ['Request', 'Application', 'User']
