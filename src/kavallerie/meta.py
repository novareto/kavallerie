import abc
import uuid
import typing as t
from dataclasses import dataclass, field
from kavallerie.pipeline import Pipeline
from kavallerie.events import Subscribers


class User(abc.ABC):
    id: str | int | uuid.UUID


class Request:

    __slots__ = ('app', 'user', 'utilities')

    app: 'Application'
    utilities: t.Mapping[str, t.Any]
    user: t.Optional[User]

    def __init__(self,
                 app: 'Application',
                 user: t.Optional[User] = None,
                 utilities: t.Optional[t.Mapping[str, t.Any]] = None):
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
