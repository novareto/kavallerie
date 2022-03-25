import inspect
import typing as t


Registry = t.TypeVar('Registry')
Component = t.TypeVar('Component')


class RegistryItem(t.NamedTuple):
    payload: t.Tuple[t.List, t.Mapping]
    value: Component


class Blueprint:
    _signature: inspect.Signature
    master: t.Type[Registry]
    handler: str
    items: t.List[RegistryItem]

    def __init__(self, master: t.Type[Registry],
                 handler: str = 'register'):
        self.items = []
        self.master = master
        self.handler = handler
        self._signature = inspect.Signature((
            param for param in inspect.signature(
                getattr(master, handler)
            ).parameters.values() if param.name != 'self'
        ))

    def add(self, payload: t.Tuple[t.List, t.Mapping], value: Component):
        self.items.append(RegistryItem(payload=payload, value=value))

    def register(self, *args, **kwargs):
        self._signature.bind(*args, **kwargs)

        def wrapper(decorated: Component):
            self.add(
                payload=tuple((args, kwargs)),
                value=decorated,
            )
            return decorated

        return wrapper

    def __iter__(self):
        return iter(self.items)

    def apply(self, registry: Registry):
        if not isinstance(registry, self.master):
            raise TypeError(
                f'Blueprint handles registration for {self.master} '
                f'got {registry.__class__!r} instead.')
        handler = getattr(registry, self.handler)
        for item in self.items:
            args, kwargs = item.payload
            handler(*args, **kwargs)(item.value)

    __call__ = apply
