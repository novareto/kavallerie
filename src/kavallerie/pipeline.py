import abc
import typing as t
import bisect
from functools import reduce
from frozen_box import freeze
from kavallerie.request import Request
from kavallerie.response import Response


Handler = t.Callable[[Request], Response]
Middleware = t.Callable[[Handler, t.Optional[t.Mapping]], Handler]


class Pipeline:

    __slots__ = ('_chain', '_by_id')

    _chain: t.List[Middleware]
    _by_id: t.Mapping

    def __init__(self):
        self._chain = []
        self._by_id = {}

    def wrap(self, wrapped: Handler, conf: t.Optional[t.Mapping] = None):
        if not self._chain:
            return wrapped

        return reduce(
            lambda x, y: y(x, conf),
            (m[1] for m in reversed(self._chain)),
            wrapped
        )

    def add(self, id: str, middleware: Middleware, order: int = 0):
        if id in self._by_id:
            raise KeyError(f"{id!r} is already registered.")

        insert = (order, middleware)
        if not self._chain:
            self._chain = [insert]
        else:
            bisect.insort(self._chain, insert)
        self._by_id[id] = insert

    def remove(self, id: str):
        if id not in self._by_id:
            raise KeyError(f"Unknown middleware {id!r}.")
        self._chain.remove(self._by_id[id])
        del self._by_id[id]

    def clear(self):
        self._chain.clear()
        self._by_id.clear()

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

    def join(self, pipeline: Pipeline, order: int = 0):
        pipeline.add(self.id, self, order)

    def leave(self, pipeline: Pipeline):
        pipeline.remove(self.id)

    @abc.abstractmethod
    def __call__(self,
                 handler: Handler,
                 appconf: t.Optional[t.Mapping] = None) -> Handler:
        pass
