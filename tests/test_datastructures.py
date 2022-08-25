import pytest
import hamcrest
from frozendict import frozendict
from kavallerie.datastructures import MultiDict


def test_data_wrong_values():

    with pytest.raises(ValueError):
        MultiDict('test')

    with pytest.raises(ValueError):
        MultiDict({"test"})

    with pytest.raises(ValueError):
        MultiDict([('a', 'b', 'c')])


def test_data_init():
    # no data
    fd = MultiDict()
    assert fd == {}

    # List of tuples
    fd = MultiDict([('a', 1), ('b', 7), ('a', -3)])
    assert fd == {'a': [1, -3], 'b': [7]}

    # tuple of tuples
    fd = MultiDict((('a', 1), ('b', 7), ('a', -3)))
    assert fd == {'a': [1, -3], 'b': [7]}

    # set of tuples: no garanteed orders
    fd = MultiDict({('a', 1), ('b', 7), ('a', -3)})
    hamcrest.assert_that(fd, hamcrest.has_entries({
        'a': hamcrest.contains_inanyorder(-3, 1),
        'b': [7]
    }))

    # dict
    fd = MultiDict({'a': 1, 'b': 7})
    assert fd == {'a': [1], 'b': [7]}

    # formdata
    fd = MultiDict([('a', 1), ('b', 7), ('a', -3)])
    fd2 = MultiDict(fd)
    assert fd is not fd2
    assert fd == fd2
    assert fd2 == {'a': [1, -3], 'b': [7]}


def test_access():
    fd = MultiDict([('a', 1), ('b', 7), ('a', -3)])
    assert fd.get('a') == 1
    assert fd.get('b') == 7
    assert fd.getlist('a') == [1, -3]
    assert fd.getlist('b') == [7]
    assert list(fd.pairs()) == [
        ('a', 1), ('a', -3), ('b', 7)
    ]


def test_casting():
    fd = MultiDict([('a', 1), ('b', 7), ('a', -3)])
    assert fd == {'a': [1, -3], 'b': [7]}

    dictified = fd.to_dict()
    hamcrest.assert_that(dictified, hamcrest.has_entries({
        'a': hamcrest.contains_inanyorder(-3, 1),
        'b': 7
    }))
    assert isinstance(dictified, frozendict)

    dictified = fd.to_dict(frozen=False)
    hamcrest.assert_that(dictified, hamcrest.has_entries({
        'a': hamcrest.contains_inanyorder(-3, 1),
        'b': 7
    }))
    assert isinstance(dictified, dict)


def test_empty_value():
    fd = MultiDict([
        ('email', 'test@example.com'), ('contact', '')])
    assert fd == {'contact': [''], 'email': ['test@example.com']}
    assert fd.to_dict() == {
        'contact': '',
        'email': 'test@example.com'
    }
