import abc
import typing as t
from functools import reduce, wraps, update_wrapper
from gelidum import freeze
from kavallerie.response import Response
from kavallerie.components import PriorityChain


Handler = t.Callable
Middleware = t.Callable[[Handler, t.Optional[t.Mapping]], Handler]
Wrapper = t.Callable[[t.Callable], t.Callable]


def chain_wrap(
        chain: t.Sequence[Wrapper], endpoint: t.Callable) -> t.Callable:
    wrapped = endpoint
    for middleware in reversed(chain):
        wrapping = middleware(wrapped)
        update_wrapper(wrapping, wrapped)
        wrapped = wrapping
    return wrapped


class Pipeline(PriorityChain[Middleware]):

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


class MiddlewareFactory(abc.ABC, Middleware):

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
