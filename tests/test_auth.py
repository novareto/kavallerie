from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.pipes.authentication import Authentication
from kavallerie.pipes.session import HTTPSession
from kavallerie.pipes.testing import DictSource


def test_auth(environ, http_session_store):

    def handler(request):
        return Response(201)

    request = Request('/', app=None, environ=environ)
    authentication = Authentication(
        sources=[DictSource({'admin': 'admin'})])
    store = http_session_store()
    session = HTTPSession(store=store, secret='my secret')

    pipeline = session(authentication(handler))
    assert pipeline(request)
    assert list(store) == []

    user = authentication.authenticator.from_credentials(request, {
        'username': 'admin',
        'password': 'admin'
    })
    assert user.id == 'admin'

    authentication.authenticator.remember(request, user)
    pipeline = session(authentication(handler))
    assert pipeline(request)
    assert list(store) == ['00000000-0000-0000-0000-000000000000']
    assert store.get('00000000-0000-0000-0000-000000000000') == {
        'user': 'admin'
    }

    authentication.authenticator.forget(request)
    pipeline = session(authentication(handler))
    assert pipeline(request)
    assert list(store) == ['00000000-0000-0000-0000-000000000000']
    assert store.get('00000000-0000-0000-0000-000000000000') == {}
