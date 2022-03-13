import uuid
from unittest.mock import patch
from horseman.response import Response
from kavallerie.session import HTTPSession
from kavallerie.flash import flash
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
def test_session_middleware(http_session_store):
    store = http_session_store()
    app = RoutingApplication()
    app.pipeline.add(
        'session', HTTPSession(store=store, secret='my secret'), order=1)
    app.pipeline.add('flash', flash, order=2)

    @app.routes.register('/add')
    def add(request):
        request.utilities['flash'].add('This is a message')
        return Response(201)

    @app.routes.register('/consume')
    def consume(request):
        messages = request.utilities['flash']
        return Response.to_json(201, body=[m.to_dict() for m in messages])

    @app.routes.register('/consume_fail')
    def consume_fail(request):
        messages = list(request.utilities['flash'])
        return Response(400)

    test = WSGIApp(app)
    response = test.get('/add')
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'flashmessages': [{'body': 'This is a message', 'type': 'info'}]
    }

    cookie = response.headers.get('Set-Cookie')
    response = test.get('/consume', headers={'Cookie': cookie})
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'flashmessages': []
    }

    response = test.get('/add', headers={'Cookie': cookie})
    cookie = response.headers.get('Set-Cookie')
    response = test.get('/consume_fail',
                        headers={'Cookie': cookie}, expect_errors=True)
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'flashmessages': [{'body': 'This is a message', 'type': 'info'}]
    }
