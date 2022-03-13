import typing as t
import urllib.parse
import horseman.meta
import horseman.parsers
from horseman.response import Response
from dataclasses import dataclass, field
from horseman.types import Environ
from roughrider.routing.components import NamedRoutes
from kavallerie.pipeline import Pipeline
from kavallerie.request import Request


@dataclass
class Application(horseman.meta.Node):
    config: dict = field(default_factory=dict)
    utilities: dict = field(default_factory=dict)
    pipeline: t.Type[Pipeline] = field(default_factory=Pipeline)
    request_factory: t.Type[Request] = Request

    def endpoint(self, request) -> Response:
        raise NotImplementedError('Implement your own.')

    def resolve(self, path: str, environ: Environ) -> Response:
        request = self.request_factory(path, self, environ)
        response = self.pipeline.wrap(self.endpoint, self.config)(request)
        return response


@dataclass
class RoutingApplication(Application):
    routes: NamedRoutes = field(default_factory=NamedRoutes)

    def endpoint(self, request):
        route = self.routes.match_method(request.path, request.method)
        request.route = route
        return route.endpoint(request, **route.params)
