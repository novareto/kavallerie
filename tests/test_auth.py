import uuid
from unittest.mock import patch
from webtest import TestApp as WSGIApp
from horseman.response import Response
from kavallerie.app import RoutingApplication
from kavallerie.pipes.session import HTTPSession
from kavallerie.pipes.authentication import Authentication
from kavallerie.pipes.testing import DictSource
from kavallerie.request import Request


def uuid_generator(count=0):
    while True:
        yield uuid.UUID(int=count)
        count += 1


def mock_uuid(generator):
    def uuid_patch():
        return next(generator)
    return uuid_patch


@patch('uuid.uuid4', mock_uuid(uuid_generator()))
def test_auth(http_session_store):

    def handler(request):
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
    middleware = HTTPSession(store=store, secret='my secret')(
        Authentication(sources=[DictSource({'admin': 'admin'})])(
            handler, {}
        ), {}
    )
    assert middleware(request)
    assert list(store) == ['00000000-0000-0000-0000-000000000000']
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'test': 1
    }
