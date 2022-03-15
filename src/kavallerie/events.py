import abc
import collections.abc
import typing as t
from inspect import isclass, signature
from roughrider.predicate.types import Predicate, Predicates
from roughrider.predicate.utils import resolve_constraints


MISSING = object()


class Event(abc.ABC):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        """This needs to be overridden in subclasses.
        """

    @classmethod
    def children(cls):
        return cls.__subclasses__()

    @classmethod
    def lineage(cls):
        for parent in cls.__mro__:
            if parent is Event:
                break
            if issubclass(parent, Event):
                yield parent

    def __repr__(self):
        lineage = ', '.join((cls.__name__ for cls in self.lineage()))
        return f"<Event({lineage})>"


Subscriber = t.Callable[[Event], t.Any]


class Subscription(t.NamedTuple):
    subscriber: Subscriber
    predicates: t.Optional[Predicates] = None

    def check(self, event: Event) -> bool:
        if self.predicates:
            return resolve_constraints(self.predicates, event)
        return None

    def __call__(self, event: Event, silence=True) -> t.Any:
        error = self.check(event)
        if error is None:
            return self.subscriber(event)
        elif not silence:
            raise error


class Subscribers(collections.abc.Collection):

    __slots__ = ('_subscribers', 'strict')

    def __init__(self, strict: bool = True):
        self.strict = strict
        self._subscribers: t.Dict[t.Type[Event], t.Set[Subscription]] = {}

    def __len__(self) -> int:
        return len(self._subscribers)

    def __contains__(self, event_type: t.Type[Event]) -> bool:
        return event_type in self._subscribers

    def __iter__(self):
        return iter(self._subscribers.items())

    def get(self, event_type: t.Type[Event]) -> Subscription:
        return self._subscribers.get(event_type)

    def add(self,
            event_type: t.Type[Event],
            subscriber: Subscriber,
            predicates: t.Optional[Predicates] = None) -> t.NoReturn:
        if self.strict:
            self.check_subscriber(event_type, subscriber)
        subscribers = self._subscribers.setdefault(event_type, set())
        subscription = Subscription(
            subscriber=subscriber,
            predicates=predicates
        )
        subscribers.add(subscription)

    def remove(self,
               event_type: t.Type[Event],
               subscriber: Subscriber) -> t.NoReturn:
        subscribers = self._subscribers[event_type]
        for subscription in list(subscribers):
            if subscription.subscriber is subscriber:
                subscribers.remove(subscription)

    def subscribe(self,
                  event_type: t.Type[Event],
                  *predicates: Predicate):
        if not predicates:
            predicates = None
        def register_subscriber(subscriber: Subscriber) -> Subscriber:
            self.add(event_type, subscriber, predicates)
            return subscriber
        return register_subscriber

    __call__ = register = subscribe

    def clear(self, event_type: t.Type[Event]):
        self._subscribers[event_type].clear()

    def notify(self, event: Event) -> t.Any:
        for event_type in event.lineage():
            if event_type in self._subscribers:
                for sub in self._subscribers[event_type]:
                    result = sub(event)
                    if result is not None:
                        return result

    @staticmethod
    def check_subscriber(event_type: t.Type[Event], sub: Subscriber):
        if not (isclass(event_type) and issubclass(event_type, Event)):
            raise KeyError('Subscriber must be a subclass of Event')
        if not isinstance(sub, t.Callable):
            raise ValueError(f'Subscriber must be a {Subscriber}')
        sig = signature(sub)
        if len(sig.parameters) != 1:
            raise TypeError('A subscriber function takes only 1 argument')
        param = list(sig.parameters.values())[0]
        if param.annotation is not param.empty and \
           not issubclass(event_type, param.annotation):
            raise TypeError(
                f'Argument {param.name!r} should hint {event_type!r} '
                f'and not {param.annotation!r}.'
            )
