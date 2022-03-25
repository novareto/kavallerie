import pytest
from unittest.mock import Mock
from kavallerie.plugins import Plugin
from kavallerie.app import Application, RoutingApplication
from kavallerie import routes as routing
from kavallerie.response import Response
from kavallerie.registries import Blueprint


def test_empty_plugin():
    plugin = Plugin('my empty plugin')
    assert plugin.dependencies == ()
    assert plugin.modules is None
    assert plugin.blueprints is None


def test_plugin_modules():
    import typing

    plugin = Plugin('my empty plugin', modules=['pytest', 'typing'])
    assert plugin.dependencies == ()
    assert plugin.modules == (pytest, typing)
    assert plugin.blueprints is None


def test_empty_lineage():
    plugin = Plugin('1')
    plugin1 = Plugin('2', dependencies=[plugin])
    plugin2 = Plugin('3', dependencies=[plugin, plugin1])
    assert plugin.__lineage__ == (plugin,)
    assert plugin1.__lineage__ == (plugin, plugin1)
    assert plugin2.__lineage__ == (plugin, plugin1, plugin2)


def test_plugin_install():
    app = Application()
    plugin = Plugin('my empty plugin')
    plugin.install(app)
    assert app.__installed_plugins__ == {'my empty plugin'}

    # No duplication.
    plugin.install(app)
    assert app.__installed_plugins__ == {'my empty plugin'}


def test_plugin_install_with_hooks():

    tracker = Mock()
    app = Application()
    plugin = Plugin('my empty plugin')

    @plugin.before_install
    def installer(plugin, app):
        tracker(plugin, app)

    plugin.install(app)
    tracker.assert_called_once_with(plugin, app)
    tracker.reset_mock()

    # Only installed once
    plugin.install(app)
    tracker.assert_not_called()


def test_plugin_with_blueprint_no_registry():
    routes = Blueprint(master=routing.Routes)
    plugin = Plugin('route', blueprints={"routes": routes})
    app = Application()

    with pytest.raises(LookupError):
        plugin.install(app)


def test_plugin_with_singular_blueprint():
    routes = Blueprint(master=routing.Routes)
    plugin = Plugin('route', blueprints={"routes": routes})
    app = RoutingApplication()

    @routes.register('/')
    def handler(request):
        return Response(200, body='ok')

    plugin.install(app)
    assert list(app.routes) == [
        routing.RouteDefinition(
            path='/',
            payload={
                'GET': routing.RouteEndpoint(
                    method='GET',
                    endpoint=handler,
                    metadata=None
                )
            }
        )
    ]


def test_plugin_with_plural_blueprints():
    browser = Blueprint(master=routing.Routes)
    api = Blueprint(master=routing.Routes)
    plugin = Plugin('route', blueprints={"routes": [browser, api]})
    app = RoutingApplication()

    @browser.register('/')
    def view(request):
        return Response(200, body='ok')

    @api.register('/api')
    def handler(request):
        return Response(200, body='ok')

    plugin.install(app)
    assert list(app.routes) == [
        routing.RouteDefinition(
            path='/',
            payload={
                'GET': routing.RouteEndpoint(
                    method='GET',
                    endpoint=view,
                    metadata=None
                )
            }
        ),
        routing.RouteDefinition(
            path='/api',
            payload={
                'GET': routing.RouteEndpoint(
                    method='GET',
                    endpoint=handler,
                    metadata=None
                )
            }
        )
    ]
