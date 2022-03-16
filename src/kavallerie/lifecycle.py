from horseman.meta import Node
from roughrider.routing.meta import Route
from kavallerie.events import Event
from kavallerie.request import Request
from kavallerie.response import Response


class RouteFound(Event):
    """Describe me.
    """
    def __init__(self, app: Node, request: Request, route: Route):
        self.app = app
        self.request = request
        self.route = route


class RequestCreated(Event):
    """Describe me.
    """

    def __init__(self, app: Node, request: Request):
        self.app = app
        self.request = request


class ResponseCreated(Event):
    """Describe me.
    """

    def __init__(self, app: Node, request: Request, response: Response):
        self.app = app
        self.request = request
        self.response = response


__all__ = ['RouteFound', 'RequestCreated', 'ResponseCreated']
