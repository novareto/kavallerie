import typing as t
import bisect
from functools import reduce


class Pipeline:

    __slots__ = ('_chain',)

    _chain: t.List[t.Callable]

    def __init__(self):
        self._chain = []

    def wrap(self, conf, wrapped):
        if not self._chain:
            return wrapped

        return reduce(
            lambda x, y: y(conf, x),
            (m[1] for m in reversed(self._chain)),
            wrapped
        )

    def add(self, middleware: t.Callable, order: int = 0):
        if not self._chain:
            self._chain = [(order, middleware)]
        else:
            bisect.insort(self._chain, (order, middleware))

    def remove(self, middleware: t.Callable, order: int = 0):
        self._chain.remove((order, middleware))

    def clear(self):
        self._chain.clear()

    def __iter__(self):
        return iter(self._chain)
