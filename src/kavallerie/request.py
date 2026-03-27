import abc
import typing as t
import urllib.parse
import horseman.parsers
import horseman.types
import horseman.datastructures
from types import SimpleNamespace
from authsources.protocols import RequestProtocol
from horseman.environ import WSGIEnvironWrapper
from horseman.mapping import Node
from http_session.session import Session
from kavallerie import meta
from kavallerie.cors import CORSPolicy


class FlagsField(SimpleNamespace):

    def __getattr__(self, name):
        return None


class Request(meta.Request, RequestProtocol, WSGIEnvironWrapper):

    __slots__ = (
        'app',
        'cors_policy',
        '_environ',
        'route',
        'user',
        'utilities',
        'flags',
    )

    # arguments
    app: Node
    flags: FlagsField
    user: meta.User | None
    cors_policy: CORSPolicy | None
    route: meta.Route | None

    def __init__(self,
                 app: meta.Application,
                 environ: horseman.types.Environ,
                 cors_policy: CORSPolicy | None = None,
                 route: meta.Route | None = None,
                 user: meta.User | None = None,
                 utilities: t.Mapping[str, t.Any] | None = None,
                 ):
        self.user = user
        self.app = app
        self.utilities = utilities is not None and utilities or {}
        self.route = route
        self.cors_policy = cors_policy
        self.flags = FlagsField()
        super().__init__(environ)

    @property
    def headers(self):
        # Respecting the RequestProtocol
        return self._environ


__all__ = ['Request']
