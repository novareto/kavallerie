import pytest
from kavallerie.contents import Model, Registry, Content


PersonSchema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
    }
}


class Person(Model):
    name: str

    def __init__(self, name):
        self.name = name

    def to_dict(self, validate=False):
        return {'name': self.name}

    @classmethod
    def from_dict(cls, data, validate=False):
        return cls(**data)

    @classmethod
    def factory(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def json_schema(cls):
        return PersonSchema


def test_empty_registry():
    reg = Registry()
    assert bool(reg) is False
    assert len(reg) == 0
    assert list(reg) == []
    assert 'test' not in reg
    assert reg.get('test') is None
    assert reg.get('test', ...) is ...

    with pytest.raises(KeyError):
        reg['test']

    with pytest.raises(KeyError):
        reg.get_schema('test')


def test_registration():
    reg = Registry()
    content = reg.add('person', Person)
    assert content == Content(
        id='person',
        schema=PersonSchema,
        model=Person,
        metadata={}
    )

    assert bool(reg) is True
    assert len(reg) == 1
    assert reg['person'] is content
    assert reg.get('person') is content
    assert list(reg) == [('person', content)]
    assert 'person' in reg
    assert reg.get_schema('person') == PersonSchema

    reg.unregister('person')
    assert bool(reg) is False
    assert len(reg) == 0
    assert list(reg) == []
    assert 'person' not in reg


def test_decorator():
    reg = Registry()
    reg.register('person', value=1)(Person)
    assert reg['person'] == Content(
        id='person',
        schema=PersonSchema,
        model=Person,
        metadata={'value': 1}
    )
