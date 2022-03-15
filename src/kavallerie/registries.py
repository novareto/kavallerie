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
