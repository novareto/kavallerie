import pytest
from kavallerie.events import Event


class ObjectCreatedEvent(Event):

    def __init__(self, request, obj):
        self.request = request
        self.obj = obj


class NonEvent:  # won't be picked up by lineage
    pass


class UserCreatedEvent(NonEvent, ObjectCreatedEvent):
    pass


def test_meta():
    with pytest.raises(TypeError):
        Event()


def test_lineage():
    assert list(ObjectCreatedEvent.lineage()) == [ObjectCreatedEvent]
    assert list(ObjectCreatedEvent.children()) == [UserCreatedEvent]

    assert list(UserCreatedEvent.lineage()) == [
        UserCreatedEvent, ObjectCreatedEvent
    ]
    assert list(UserCreatedEvent.children()) == []


def test_repr():
    event = UserCreatedEvent({}, 'John')
    assert repr(event) == "<Event(UserCreatedEvent, ObjectCreatedEvent)>"
