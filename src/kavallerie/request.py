import typing as t
import urllib.parse
import functools
import horseman.parsers
import horseman.types
import horseman.http
import horseman.meta
from dataclasses import dataclass
from roughrider.routing.meta import Route


class Request(horseman.meta.Overhead):

    __slots__ = (
        '_content_type',
        '_cookies',
        '_data',
        '_query',
        'app',
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
    query: horseman.http.Query
    route: t.Optional[Route]
    script_name: str

    _data: t.Optional[horseman.parsers.Data]

    def __init__(self,
                 app: horseman.meta.Node,
                 environ: horseman.types.Environ,
                 route: t.Optional[Route] = None):
        self._content_type = ...
        self._cookies = ...
        self._data = ...
        self._query = ...
        self.app = app
        self.environ = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.script_name = urllib.parse.quote(environ['SCRIPT_NAME'])

    def extract(self) -> horseman.parsers.Data:
        if self._data is not ...:
            return self._data

        if self.content_type:
            self._data = horseman.parsers.parser(
                self.environ['wsgi.input'], self.content_type)

        return self._data

    @property
    def query(self):
        if self._query is ...:
            self._query = horseman.http.Query.from_environ(self.environ)
        return self._query

    @property
    def cookies(self):
        if self._cookies is ...:
            self._cookies = horseman.http.Cookies.from_environ(self.environ)
        return self._cookies

    @property
    def content_type(self):
        if self._content_type is ...:
            if 'CONTENT_TYPE' in self.environ:
                self._content_type = \
                    horseman.http.ContentType.from_http_header(
                        self.environ['CONTENT_TYPE'])
            else:
                self._content_type = None
        return self._content_type

    @functools.cached_property
    def application_uri(self):
        scheme = self.environ['wsgi.url_scheme']
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
            qs = urllib.parse.quote(self.environ.get('QUERY_STRING'))
            if qs:
                return f"{url}{path_info}?{qs}"
        return f"{url}{path_info}"
