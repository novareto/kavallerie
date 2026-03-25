import typing as t
import horseman.parsers
from dataclasses import dataclass, field
from horseman.exceptions import HTTPError
from horseman.mapping import RootNode
from horseman.types import Environ, ExceptionInfo
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.events import Subscribers
from kavallerie.routes import Routes
from kavallerie import meta


@dataclass
class Application(meta.Application, RootNode):
    request_factory: t.Type[Request] = Request

    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        cls, exc, tb = exc_info
        if isinstance(exc, HTTPError):
            return Response(exc.status, body=exc.body)

    def endpoint(self, request) -> Response:
        raise NotImplementedError('Implement your own.')

    def resolve(self, environ: Environ) -> Response:
        request = self.request_factory(self, environ)
        endpoint = self.pipeline.wrap(self.endpoint, self.config)
        return endpoint(request)


@dataclass
class RoutingApplication(Application):
    routes: Routes = field(default_factory=Routes)

    def endpoint(self, request: Request) -> Response:
        route = self.routes.match_method(request.path, request.method)
        if route is None:
            raise HTTPError(404)

        request.route = route
        return route.endpoint(request, **route.params)
