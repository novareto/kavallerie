import pytest
from kavallerie.plugins import Plugin, Plugins
from kavallerie.app import Application


def test_plugins_dependencies_order():
    transaction = Plugin('transaction')
    sql = Plugin('sql', dependencies=[transaction])
    myplugin = Plugin('myplugin', dependencies=[sql])
    plugins = Plugins([myplugin])

    assert plugins.ordered == ('transaction', 'sql', 'myplugin')


def test_unknown_dependency():
    plugins = Plugins([])
    with pytest.raises(LookupError):
        plugins.apply(None, 'unknown')


def test_plugins_dependencies():
    useless = Plugin('useless')
    transaction = Plugin('transaction')
    sql = Plugin('sql', dependencies=[transaction])
    myplugin = Plugin('myplugin', dependencies=[sql])
    plugins = Plugins([myplugin, useless])

    assert plugins.ordered == ('transaction', 'sql', 'useless', 'myplugin')

    app = Application()
    plugins.apply(app, 'myplugin', 'useless')
    assert app.__installed_plugins__ == {
        'sql', 'useless', 'transaction', 'myplugin'
    }
