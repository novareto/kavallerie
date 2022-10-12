import abc
import typing as t
import bisect
from functools import reduce, wraps
from gelidum import freeze
from kavallerie.response import Response


Handler = t.Callable
Middleware = t.Callable[[Handler, t.Optional[t.Mapping]], Handler]


class Pipeline:

    __slots__ = ('_chain',)

    _chain: t.List[Middleware]

    def __init__(self, *middlewares):
        self._chain = list(enumerate(middlewares))

    def wrap(self, wrapped: Handler, conf: t.Optional[t.Mapping] = None):
        if not self._chain:
            return wrapped

        return reduce(
            lambda x, y: y(x, conf),
            (m[1] for m in reversed(self._chain)),
            wrapped
        )

    def __call__(self, conf: t.Optional[t.Mapping] = None):
        def wrapper(wrapped: Handler):
            return self.wrap(wrapped, conf)
        return wrapper

    def add(self, middleware: Middleware, order: int = 0):
        insert = (order, middleware)
        if not self._chain:
            self._chain = [insert]
        elif insert in self._chain:
            raise KeyError(
                'Middleware {middleware!r} already exists at #{order}.')
        else:
            bisect.insort(self._chain, insert)

    def remove(self, middleware: Middleware, order: int):
        insert = (order, middleware)
        if insert not in self._chain:
            raise KeyError(
                'Middleware {middleware!r} doest not exist at #{order}.')
        self._chain.remove((order, middleware))

    def clear(self):
        self._chain.clear()

    def __iter__(self):
        return iter(self._chain)


class MiddlewareFactory(abc.ABC, Middleware):

    id: t.ClassVar[str]
    Configuration: t.ClassVar[t.Type] = None

    def __init__(self, **kwargs):
        if self.Configuration is not None:
            self.config = self.Configuration(**kwargs)
        else:
            self.config = freeze(kwargs)
        self.__post_init__()

    def __post_init__(self):
        pass

    @abc.abstractmethod
    def __call__(self,
                 handler: Handler,
                 appconf: t.Optional[t.Mapping] = None) -> Handler:
        pass
