import hamcrest
from horseman.response import Response
from kavallerie.app import RoutingApplication
from kavallerie.pipes.flash import flash
from kavallerie.pipes.session import HTTPSession

from webtest import TestApp as WSGIApp


def test_session_middleware(http_session_store):
    store = http_session_store()
    app = RoutingApplication()
    app.pipeline.add(HTTPSession(store=store, secret='my secret'), order=1)
    app.pipeline.add(flash, order=2)

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
        list(request.utilities['flash'])
        return Response(400)

    test = WSGIApp(app)
    response = test.get('/add')
    session = store.get('00000000-0000-0000-0000-000000000000')
    hamcrest.assert_that(session, hamcrest.has_entries({
        'flashmessages': [{'body': 'This is a message', 'type': 'info'}]
    }))

    cookie = response.headers.get('Set-Cookie')
    response = test.get('/consume', headers={'Cookie': cookie})
    session = store.get('00000000-0000-0000-0000-000000000000')
    hamcrest.assert_that(session, hamcrest.has_entries({
        'flashmessages': []
    }))

    response = test.get('/add', headers={'Cookie': cookie})
    cookie = response.headers.get('Set-Cookie')
    response = test.get('/consume_fail',
                        headers={'Cookie': cookie}, expect_errors=True)
    session = store.get('00000000-0000-0000-0000-000000000000')
    hamcrest.assert_that(session, hamcrest.has_entries({
        'flashmessages': [{'body': 'This is a message', 'type': 'info'}]
    }))
