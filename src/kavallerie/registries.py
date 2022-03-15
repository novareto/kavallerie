import typing as t
import inspect
import decorated_registry
from typing import Dict, TypeVar, Optional


Component = TypeVar('Component')


class NamedComponents(Dict[str, Component]):

    def __init__(self, items: Optional[Dict[str, Component]] = None):
        if items is not None:
            if not all(isinstance(key, str) for key in items):
                raise TypeError('All keys must be strings.')
            super().__init__(items)

    def register(self, component: Component, name: str):
        self[name] = component

    def component(self, name: str):
        """Component decorator
        """
        def register_component(component: Component) -> Component:
            self.register(component, name)
            return component

        return register_component

    def unregister(self, name: str) -> None:
        del self[name]

    def __add__(self, components: dict):
        return self.__class__({**self, **components})

    def __setitem__(self, name: str, component: Component):
        if not isinstance(name, str):
            raise TypeError('Key must be a string.')
        return super().__setitem__(name, component)


class DelegatedRegistry:

    _registry: decorated_registry.Registry
    _signature: inspect.Signature
    delegate_for: t.Type
    handler: str

    def __init__(self, delegate_for: t.Type, handler: str = 'register'):
        self._registry = decorated_registry.Registry()
        self.delegate_for = delegate_for
        self.handler = handler
        self._signature = inspect.Signature(
            (param for param in
             inspect.signature(
                 getattr(delegate_for, self.handler)).parameters.values()
             if param.name != 'self')
        )

    def register(self, *args, **kwargs):
        self._signature.bind(*args, **kwargs)

        def wrapper(decorated_):
            return self._registry.decorate(
                payload=tuple((args, kwargs)),
                value=decorated_,
            )

        return wrapper

    def __iter__(self):
        return iter(self._registry.items)

    def apply(self, registry):
        assert isinstance(registry, self.delegate_for)
        handler = getattr(registry, self.handler)
        for item in self._registry.items:
            args, kwargs = item.payload
            handler(*args, **kwargs)(item.value)
