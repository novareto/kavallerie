import abc
import uuid
import typing as t
from dataclasses import dataclass, field
from authsources.identity import User
from horseman.abc.request import RequestProtocol
from horseman.abc.response import ResponseProtocol
from horseman.request import Request as BaseRequest
from kettu.types import HTTPMethod
from horseman.types import WSGICallable
from kavallerie.events import Subscribers
from kavallerie.pipeline import Pipeline
from kavallerie.errors import HTTPError


Endpoint = t.Callable[[RequestProtocol], WSGICallable]
HTTPMethods = t.Iterable[HTTPMethod]


class APIView:
    """View with methods to act as HTTP METHOD dispatcher.
    Method names of the class must be a valid uppercase HTTP METHOD name.
    example : OPTIONS, GET, POST
    """

    def __call__(self, request: RequestProtocol) -> ResponseProtocol:
        if worker := getattr(self, request.method, None):
            return worker(request)

        # Method not allowed
        raise HTTPError(405)


class Request(BaseRequest):

    __slots__ = ('app', 'user', 'utilities')

    app: t.Optional['Application']
    utilities: t.Mapping[str, t.Any]
    user: User | None

    def __init__(self,
                 app: t.Optional['Application'] = None,
                 user: User | None = None,
                 utilities: t.Mapping[str, t.Any] | None = None):
        self.app = app
        self.user = user
        self.utilities = utilities is not None and utilities or {}


@dataclass
class Application:
    utilities: dict = field(default_factory=dict)
    config: t.Mapping[str, t.Any] = field(default_factory=dict)
    subscribers: Subscribers = field(default_factory=Subscribers)
    request_factory: t.Callable[..., Request] = Request
    pipeline: Pipeline = field(default_factory=Pipeline)


__all__ = ['Request', 'Application', 'User']
