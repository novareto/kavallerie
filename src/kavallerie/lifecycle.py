import typing as t
from kavallerie.events import Event
from kavallerie.request import Request, User


class UserEvent(Event):

    def __init__(
            self,
            user: User,
            request: t.Optional[Request] = None,
            context: t.Optional[t.Mapping] = None):
        self.user = user
        self.request = request
        self.context = context


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

    def __init__(self, obj, data, request: t.Optional[Request] = None):
        self.obj = obj
        self.data = data
        self.request = request


class ObjectRemovedEvent(ObjectEvent):
    pass
