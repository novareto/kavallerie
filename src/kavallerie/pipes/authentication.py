import typing as t
from pathlib import PurePosixPath
from kavallerie.response import Response
from kavallerie.request import Request
from kavallerie.auth import Source, Authenticator
from kavallerie.pipeline import Handler, MiddlewareFactory


Filter = t.Callable[[Handler, Request], t.Optional[Response]]


class Authentication(MiddlewareFactory):

    class Configuration(t.NamedTuple):
        authenticator: Authenticator
        filters: t.Optional[t.Iterable[Filter]] = None

    def __post_init__(self):
        self.authenticator = self.config.authenticator

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def authentication_middleware(request):
            assert isinstance(request, Request)
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


def security_bypass(urls: t.List[str]) -> Filter:
    unprotected = frozenset(
        PurePosixPath(bypass) for bypass in urls
    )
    def _filter(caller, request):
        path = PurePosixPath(request.path)
        for bypass in unprotected:
            if path.is_relative_to(bypass):
                return caller(request)

    return _filter


def secured(path: str) -> Filter:

    def _filter(caller, request):
        if request.user is None:
            return Response.redirect(request.script_name + path)

    return _filter


def TwoFA(path: str, checker: t.Callable[[Request], bool]) -> Filter:

    def _filter(caller, request):
        if request.path == path:
            return caller(request)
        if not checker(request):
            return Response.redirect(request.script_name + path)

    return _filter
