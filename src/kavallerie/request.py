import abc
import typing as t
import urllib.parse
import horseman.parsers
import horseman.types
import horseman.http
import horseman.meta
from horseman.parsers import Data
from http_session.session import Session
from roughrider.routing.meta import Route
from roughrider.cors.policy import CORSPolicy
from kavallerie.utils import unique
from kavallerie.datastructures import TypeCastingDict
from kavallerie import meta
from kavallerie.meta import User  # backward compatibility


class Query(TypeCastingDict):

    @classmethod
    def from_value(cls, value: str):
        return cls(urllib.parse.parse_qsl(
            value, keep_blank_values=True, strict_parsing=True))

    @classmethod
    def from_environ(cls, environ: dict):
        qs = environ.get('QUERY_STRING', '')
        if qs:
            return cls.from_value(qs)
        return cls()


class Request(meta.Request, horseman.meta.Overhead):

    __slots__ = meta.Request.__slots__ + (
        '_data',
        'cors_policy',
        'environ',
        'method',
        'route',
        'script_name',
    )

    app: horseman.meta.Node
    content_type: t.Optional[horseman.http.ContentType]
    cookies: horseman.http.Cookies
    environ: horseman.types.Environ
    method: horseman.types.HTTPMethod
    path: str
    query: Query
    script_name: str
    cors_policy: t.Optional[CORSPolicy]
    route: t.Optional[Route]
    _data: t.Optional[horseman.parsers.Data]

    def __init__(self, app,
                 environ: horseman.types.Environ,
                 cors_policy: t.Optional[CORSPolicy] = None,
                 route: t.Optional[Route] = None,
                 **kwargs
                 ):
        meta.Request.__init__(self, app, **kwargs)
        self._data = ...
        self.environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()
        self.route = route
        self.cors_policy = cors_policy
        self.script_name = urllib.parse.quote(
            environ.get('SCRIPT_NAME', '')
        )

    def extract(self) -> horseman.parsers.Data:
        if self._data is not ...:
            return self._data

        if self.content_type:
            self._data = horseman.parsers.parser(
                self.environ['wsgi.input'], self.content_type)
        else:
            self._data = Data()
        return self._data

    @unique
    def path(self):
        if path := self.environ.get('PATH_INFO'):
            return path.encode('latin-1').decode('utf-8')
        return '/'

    @unique
    def query(self):
        return Query.from_environ(self.environ)

    @unique
    def cookies(self):
        return horseman.http.Cookies.from_environ(self.environ)

    @unique
    def content_type(self):
        if 'CONTENT_TYPE' in self.environ:
            return horseman.http.ContentType.from_http_header(
                self.environ['CONTENT_TYPE'])

    @unique
    def application_uri(self):
        scheme = self.environ.get('wsgi.url_scheme', 'http')
        http_host = self.environ.get('HTTP_HOST')
        if not http_host:
            server = self.environ['SERVER_NAME']
            port = self.environ.get('SERVER_PORT', '80')
        elif ':' in http_host:
            server, port = http_host.split(':', 1)
        else:
            server = http_host
            port = '80'

        if (scheme == 'http' and port == '80') or \
           (scheme == 'https' and port == '443'):
            return f'{scheme}://{server}{self.script_name}'
        return f'{scheme}://{server}:{port}{self.script_name}'

    def uri(self, include_query=True):
        url = self.application_uri
        path_info = urllib.parse.quote(self.environ.get('PATH_INFO', ''))
        if include_query:
            qs = urllib.parse.quote(self.environ.get('QUERY_STRING', ''))
            if qs:
                return f"{url}{path_info}?{qs}"
        return f"{url}{path_info}"


__all__ = ['Request', 'Query']
