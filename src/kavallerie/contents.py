import typing as t
import collections.abc
from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass


JSONValue = t.Union[
    str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]
]
JSONType = t.Union[t.Dict[str, JSONValue], t.List[JSONValue]]


class Model(ABC):

    __metadata__: dict

    @classmethod
    def json_schema(cls) -> t.Optional[JSONType]:
        return None

    @abstractmethod
    def to_dict(self, validate: bool = False) -> t.Dict:
        pass

    @abstractclassmethod
    def factory(cls, data: dict, validate: bool = False) -> 'Model':
        """Returns a fully fledged model from a dict of attributes values.
        Values in data that do not belong to the model should be overlooked
        or put into __metadata__.
        """


@dataclass
class Content:
    id: str
    model: Model
    schema: t.Optional[JSONType] = None
    metadata: t.Optional[t.Mapping] = None


class Registry(collections.abc.Collection):

    _store: t.Dict[str, Content]

    def __init__(self):
        self._store = {}

    def __bool__(self):
        return bool(self._store)

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store.items())

    def __contains__(self, name: str):
        return name in self._store

    def __getitem__(self, name: str):
        return self._store[name]

    def register(self, name: str, **metadata):
        def model_registration(model: Model) -> Model:
            self.register(name, model, metadata)
            return model
        return model_registration

    def add(self, name: str,
            model: Model,
            metadata: t.Mapping = None) -> Content:
        if metadata is None:
            metadata = {}
        content = Content(
            id=name,
            schema=model.json_schema(),
            model=model,
            metadata=metadata
        )
        self._store[name] = content
        return content

    def unregister(self, name: str) -> t.NoReturn:
        del self._store[name]

    remove = unregister

    def get(self, name: str, default: t.Any = None) -> t.Any:
        return self._store.get(name, default)

    def get_schema(self, name: str) -> t.Optional[JSONType]:
        if name not in self._store:
            raise KeyError(name)
        return self._store[name].schema
