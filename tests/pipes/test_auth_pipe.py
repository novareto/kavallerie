from freezegun import freeze_time
from kavallerie.meta import User
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.testing import DictSource
from kavallerie.pipes.session import HTTPSession
from kavallerie.auth import HTTPSessionAuthenticator
from kavallerie.pipes.authentication import Authentication


def test_auth(environ, http_session_store):

    def handler(request):
        return Response(201)

    with freeze_time('2024-11-26 12:00:01'):
        request = Request(None, environ=environ)
        authentication = Authentication(
            authenticator=HTTPSessionAuthenticator(
                sources=[DictSource({'admin': 'admin'})]
            )
        )
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
            'user': 'admin',
            'created': 1732622401,
            'expires': 1732622701,
        }

    authentication.authenticator.forget(request)
    pipeline = session(authentication(handler))

    with freeze_time('2024-11-26 12:00:01'):
        assert pipeline(request)
        assert list(store) == ['00000000-0000-0000-0000-000000000000']
        assert store.get('00000000-0000-0000-0000-000000000000') == {}
