from horseman.response import Response
from kavallerie.app import RoutingApplication
from kavallerie.pipes.session import HTTPSession
from kavallerie.request import Request

from webtest import TestApp as WSGIApp


def test_session(environ, http_session_store):

    def handler(request):
        request.utilities['http_session']['test'] = 1
        return Response(201)

    request = Request('/', app=None, environ=environ)
    store = http_session_store()
    middleware = HTTPSession(store=store, secret='my secret')(handler)
    assert middleware(request)
    assert list(store) == ['00000000-0000-0000-0000-000000000000']
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'test': 1
    }


def test_session_middleware(http_session_store):
    store = http_session_store()
    app = RoutingApplication()
    app.pipeline.add(HTTPSession(store=store, secret='my secret'))

    @app.routes.register('/add')
    def add(request):
        request.utilities['http_session']['value'] = 1
        return Response(201)

    @app.routes.register('/change')
    def change(request):
        request.utilities['http_session']['value'] = 42
        return Response(201)

    @app.routes.register('/fail')
    def failer(request):
        request.utilities['http_session']['value'] = 666
        return Response(400)

    @app.routes.register('/except')
    def exception(request):
        request.utilities['http_session']['value'] = 666
        raise NotImplementedError()

    test = WSGIApp(app)
    response = test.get('/add')
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'value': 1
    }

    cookie = response.headers.get('Set-Cookie')
    response = test.get('/change', headers={'Cookie': cookie})
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'value': 42
    }

    cookie = response.headers.get('Set-Cookie')
    response = test.get(
        '/fail', headers={'Cookie': cookie}, expect_errors=True)
    assert response.status_code == 400
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'value': 42
    }
