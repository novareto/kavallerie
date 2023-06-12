import bisect
import typing as t


I = t.TypeVar('I')


class PriorityChain(t.Generic[I]):

    __slots__ = ('_chain',)

    _chain: t.List[t.Tuple[int, I]]

    def __init__(self, *items: I):
        self._chain = list(enumerate(items))

    def __iter__(self):
        return iter(self._chain)

    def add(self, item: I, order: int = 0):
        insert = (order, item)
        if not self._chain:
            self._chain = [insert]
        elif insert in self._chain:
            raise KeyError('Item {item!r} already exists at #{order}.')
        else:
            bisect.insort(self._chain, insert)

    def remove(self, item: I, order: int):
        insert = (order, item)
        if insert not in self._chain:
            raise KeyError('Item {item!r} doest not exist at #{order}.')
        self._chain.remove(insert)

    def clear(self):
        self._chain.clear()
