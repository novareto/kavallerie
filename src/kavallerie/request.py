import abc
import typing as t
import urllib.parse
import horseman.parsers
import horseman.types
import horseman.datastructures
from horseman.environ import WSGIEnvironWrapper
from horseman.mapping import Node
from functools import cached_property
from http_session.session import Session
from roughrider.cors.policy import CORSPolicy
from kavallerie.datastructures import TypeCastingDict
from kavallerie import meta


class Request(meta.Request, WSGIEnvironWrapper):

    __slots__ = (
        'app',
        'cors_policy',
        'environ',
        'method',
        'route',
        'script_name',
        'user',
        'utilities',
    )

    # arguments
    app: Node
    environ: horseman.types.Environ
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
        self._data = None
        self.user = user
        self.app = app
        self.utilities = utilities is not None and utilities or {}
        self._environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()
        self.route = route
        self.cors_policy = cors_policy
        self.script_name = urllib.parse.quote(
            environ.get('SCRIPT_NAME', '')
        )


__all__ = ['Request', 'Query']
