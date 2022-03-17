import typing as t
from horseman.meta import Node
from kavallerie.events import Event
from kavallerie.request import Request, User
from kavallerie.response import Response
from roughrider.routing.meta import Route


class RouteFound(Event):

    def __init__(self, app: Node, request: Request, route: Route):
        self.app = app
        self.route = route
        self.request = request


class RequestCreated(Event):

    def __init__(self, app: Node, request: Request):
        self.app = app
        self.request = request


class ResponseCreated(Event):

    def __init__(self, app: Node, request: Request, response: Response):
        self.app = app
        self.request = request
        self.response = response


class UserEvent(Event):

    def __init__(
            self,
            user: User,
            request: Optional[Request] = None,
            **namespace: Any):
        self.user = user
        self.request = request
        self.namespace = namespace


class UserLoggedInEvent(UserEvent):
    pass


class UserRegisteredEvent(UserEvent):
    pass


class ObjectEvent(Event):

    def __init__(self, obj: t.Any, request: t.Optional[Request] = None):
        self.obj = obj
        self.request = request


class ObjectCreatedEvent(ObjectEvent):
    pass


class ObjectAddedEvent(ObjectEvent):
    pass


class ObjectModifiedEvent(ObjectEvent):

    def __init__(self, obj, data, request: Optional[Request] = None):
        self.obj = obj
        self.data = data
        self.request = request


class ObjectRemovedEvent(ObjectEvent):
    pass
