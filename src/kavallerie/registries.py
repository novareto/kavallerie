import typing as t
import inspect


Registry = t.TypeVar('Registry')
Component = t.TypeVar('Component')


class NamedComponents(t.Dict[str, Component]):

    def __init__(self, items: t.Optional[t.Mapping[str, Component]] = None):
        if items is not None:
            if not all(isinstance(key, str) for key in items):
                raise TypeError('All keys must be strings.')
            super().__init__(items)

    def add(self, name: str, component: Component):
        self[name] = component

    def register(self, name: str):
        """Component decorator
        """
        def register_component(component: Component) -> Component:
            self.add(name, component)
            return component

        return register_component

    def __add__(self, components: t.Mapping):
        return self.__class__({**self, **components})

    def __setitem__(self, name: str, component: Component):
        if not isinstance(name, str):
            raise TypeError('Key must be a string.')
        return super().__setitem__(name, component)


class RegistryItem(t.NamedTuple):
    payload: t.Tuple[t.List, t.Mapping]
    value: Component


class DelegatedRegistry:
    _signature: inspect.Signature
    delegate_for: t.Type[Registry]
    handler: str
    items: t.List[RegistryItem]

    def __init__(self, delegate_for: t.Type[Registry],
                 handler: str = 'register'):
        self.items = []
        self.delegate_for = delegate_for
        self.handler = handler
        self._signature = inspect.Signature((
            param for param in inspect.signature(
                getattr(delegate_for, handler)
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
        if not isinstance(registry, self.delegate_for):
            raise TypeError(
                f'Registry handles delegation for {self.delegate_for} '
                f'got {registry.__class__!r} instead.')
        handler = getattr(registry, self.handler)
        for item in self.items:
            args, kwargs = item.payload
            handler(*args, **kwargs)(item.value)
