import pytest
from kavallerie.plugins import Plugin, Plugins
from kavallerie.app import Application


def test_unknown_dependency():
    plugins = Plugins([])
    with pytest.raises(LookupError):
        plugins.install_by_name(None, 'unknown')


def test_plugins_dependencies():
    useless = Plugin('useless')
    transaction = Plugin('transaction')
    sql = Plugin('sql', dependencies=[transaction])
    myplugin = Plugin('myplugin', dependencies=[sql])
    plugins = Plugins([myplugin, useless])

    app = Application()
    plugins.install_by_name(app, 'myplugin', 'useless')
    assert app.__installed_plugins__ == {
        'sql', 'useless', 'transaction', 'myplugin'
    }


def test_plugins_from_entrypoints():
    plugins = Plugins.from_entrypoints()
    assert plugins._store == {}
