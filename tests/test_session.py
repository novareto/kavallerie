import uuid
from unittest.mock import patch
from horseman.response import Response
from kavallerie.request import Request
from kavallerie.session import HTTPSession
from kavallerie.app import RoutingApplication
from webtest import TestApp as WSGIApp


def uuid_generator(count=0):
    while True:
        yield uuid.UUID(int=count)
        count += 1


def mock_uuid(generator):
    def uuid_patch():
        return next(generator)
    return uuid_patch


@patch('uuid.uuid4', mock_uuid(uuid_generator()))
def test_session(http_session_store):

    def handler(request):
        request.utilities['http_session']['test'] = 1
        return Response(201)

    request = Request(
        '/', app=None,
        environ={
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'HTTP_HOST': 'localhost:80'
        }
    )
    store = http_session_store()
    middleware = HTTPSession(store=store, secret='my secret')(handler, {})
    assert middleware(request)
    assert list(store) == ['00000000-0000-0000-0000-000000000000']
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'test': 1
    }


@patch('uuid.uuid4', mock_uuid(uuid_generator()))
def test_session_middleware(http_session_store):
    store = http_session_store()
    app = RoutingApplication()
    HTTPSession(store=store, secret='my secret').join(app.pipeline)

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
    response = test.get('/fail', headers={'Cookie': cookie}, expect_errors=True)
    assert response.status_code == 400
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'value': 42
    }

    # cookie = response.headers.get('Set-Cookie')
    # response = test.get('/except', headers={'Cookie': cookie}, expect_errors=True)
    # assert response.status_code == 400
    # assert store.get('00000000-0000-0000-0000-000000000000') == {
    #     'value': 42
    # }
