import typing as t
import horseman.parsers
from dataclasses import dataclass, field
from horseman.mapping import RootNode
from horseman.types import WSGIEnviron, ExceptionInfo
from kavallerie import meta
from kavallerie.errors import HTTPError
from kavallerie.events import Subscribers
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.routing import Router


@dataclass
class Application(meta.Application, RootNode):
    request_factory: t.Type[Request] = Request

    def handle_exception(self, exc_info: ExceptionInfo, environ: WSGIEnviron):
        cls, exc, tb = exc_info
        if isinstance(exc, HTTPError):
            return Response(exc.status, body=exc.body)

    def endpoint(self, request) -> Response:
        raise NotImplementedError('Implement your own.')

    def resolve(self, environ: WSGIEnviron) -> Response:
        request = self.request_factory(self, environ)
        endpoint = self.pipeline.wrap(self.endpoint, self.config)
        return endpoint(request)

    def finalize(self):
        return self


@dataclass
class RoutingApplication(Application):
    routes: Router = field(default_factory=Router)

    def endpoint(self, request: Request) -> Response:
        route = self.routes.get(request.path, request.method)
        if route is None:
            raise HTTPError(404)

        request.route = route
        return route.routed(request, **route.params)

    def finalize(self):
        self.routes.finalize()
        return self
