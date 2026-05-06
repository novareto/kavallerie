import typing as t
from horseman.types import WSGIEnviron
from types import SimpleNamespace
from horseman.mapping import Node
from http_session.session import Session
from kavallerie import meta
from kettu.cors import CORSPolicy
from autorouting import Route


class FlagsField(SimpleNamespace):

    def __getattr__(self, name):
        return None


class Request(meta.Request):

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
    flags: FlagsField
    cors_policy: CORSPolicy | None
    route: Route | None
    environ: WSGIEnviron

    def __init__(self,
                 app: meta.Application | None,
                 environ: WSGIEnviron,
                 *,
                 cors_policy: CORSPolicy | None = None,
                 route: Route | None = None,
                 user: meta.User | None = None,
                 utilities: t.Mapping[str, t.Any] | None = None,
                 ):
        self.route = route
        self.cors_policy = cors_policy
        self.flags = FlagsField()
        self.environ = environ
        super().__init__(app=app, user=user, utilities=utilities)

    @property
    def headers(self):
        # Respecting the RequestProtocol
        return self.environ


__all__ = ['Request']
