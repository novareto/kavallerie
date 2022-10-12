import typing as t
import horseman.meta
import horseman.parsers
from dataclasses import dataclass, field
from horseman.http import HTTPError
from horseman.types import Environ, ExceptionInfo
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.events import Subscribers
from kavallerie.routes import Routes
from kavallerie import meta


@dataclass
class Application(meta.Application, horseman.meta.SentryNode):
    request_factory: t.Type[Request] = Request

    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        pass

    def endpoint(self, request) -> Response:
        raise NotImplementedError('Implement your own.')

    def resolve(self, path: str, environ: Environ) -> Response:
        request = self.request_factory(self, environ)
        request.path = path
        return self.pipeline.wrap(self.endpoint, self.config)(request)


@dataclass
class RoutingApplication(Application):
    routes: Routes = field(default_factory=Routes)

    def endpoint(self, request) -> Response:
        route = self.routes.match_method(request.path, request.method)
        if route is None:
            raise HTTPError(404)
        request.route = route
        return route.endpoint(request, **route.params)
