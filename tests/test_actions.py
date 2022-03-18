import pytest
from kavallerie.actions import ActionStore, Action
from prejudice.errors import ConstraintsErrors, ConstraintError


def test_attributes():
    action = Action(
        name="test",
        title="test",
        resolve=None,
        attributes={'class': 'my_css_class'},
        classifiers=frozenset()
    )
    assert action.attributes == {'class': 'my_css_class'}


def test_no_evaluate():
    action = Action(
        name="test",
        title="test",
        resolve=None,
        classifiers=frozenset()
    )
    assert action.evaluate() is None


def test_evaluate():

    def name_is_not_test(action):
        if action.name == 'test':
            raise ConstraintError('Name should not be "test".')

    action = Action(
        name="test",
        title="test",
        resolve=None,
        classifiers=frozenset(),
        conditions=(name_is_not_test,)
    )
    assert action.evaluate() == ConstraintsErrors(
        ConstraintError(message='Name should not be "test".')
    )


def test_evaluate_namespace():

    def admin_only(action, user):
        if user != 'admin':
            raise ConstraintError('User should be "admin".')

    action = Action(
        name="test",
        title="test",
        resolve=None,
        classifiers=frozenset(),
        conditions=(admin_only,)
    )
    assert action.evaluate(user='test') == ConstraintsErrors(
        ConstraintError(message='User should be "admin".')
    )
    assert action.evaluate(user='admin') is None


def test_empty():
    actions = ActionStore()
    assert isinstance(actions, dict)
    assert len(actions) == 0
    assert list(actions.values()) == []


def test_registration_override():
    actions = ActionStore()

    @actions.register("someid")
    def my_action():
        return "yeah"

    assert len(actions) == 1
    assert list(actions.values()) == [
        Action(
            name='someid',
            title=None,
            resolve=my_action,
            classifiers=frozenset()
        )
    ]

    @actions.register("someid")
    def my_other_action():
        return "yeah"

    assert len(actions) == 1
    assert list(actions.values()) == [
        Action(
            name='someid',
            title=None,
            resolve=my_other_action,
            classifiers=frozenset()
        )
    ]


def test_classifiers_partial():

    actions = ActionStore()

    @actions.register(
        "satay", title="Satay Soup", classifiers=('soup', 'phô'))
    def vietnamese_soup_with_peanuts():
        return "yummy"

    assert len(actions) == 1

    with pytest.raises(KeyError):
        list(actions.partial())

    found = actions.partial('bobun')
    assert list(found) == []

    found = actions.partial('soup')
    assert list(found) == [Action(
        name='satay',
        title="Satay Soup",
        resolve=vietnamese_soup_with_peanuts,
        classifiers=frozenset({'soup', 'phô'})
    )]

    found = actions.partial('soup', 'phô')
    assert list(found) == [Action(
        name='satay',
        title="Satay Soup",
        resolve=vietnamese_soup_with_peanuts,
        classifiers=frozenset({'soup', 'phô'})
    )]


def test_classifiers_one_of():

    actions = ActionStore()

    @actions.register(
        "satay", title="Satay Soup", classifiers=('soup', 'phô'))
    def vietnamese_soup_with_peanuts():
        return "yummy"

    with pytest.raises(KeyError):
        list(actions.one_of())

    assert list(actions.one_of('bobun')) == []

    found = actions.one_of('soup', 'bobun', 'beef')
    assert list(found) == [Action(
        name='satay',
        title="Satay Soup",
        resolve=vietnamese_soup_with_peanuts,
        classifiers=frozenset({'soup', 'phô'})
    )]

    found = actions.one_of('soup', 'phô')
    assert list(found) == [Action(
        name='satay',
        title="Satay Soup",
        resolve=vietnamese_soup_with_peanuts,
        classifiers=frozenset({'soup', 'phô'})
    )]


def test_classifiers_exact():

    actions = ActionStore()

    @actions.register(
        "satay", title="Satay Soup", classifiers=('soup', 'phô'))
    def vietnamese_soup_with_peanuts():
        return "yummy"

    with pytest.raises(KeyError):
        list(actions.exact())

    assert list(actions.exact('bobun')) == []
    assert list(actions.exact('soup', 'bobun', 'beef')) == []
    assert list(actions.exact('soup')) == []

    found = actions.exact('soup', 'phô')
    assert list(found) == [Action(
        name='satay',
        title="Satay Soup",
        resolve=vietnamese_soup_with_peanuts,
        classifiers=frozenset({'soup', 'phô'})
    )]
