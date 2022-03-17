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
