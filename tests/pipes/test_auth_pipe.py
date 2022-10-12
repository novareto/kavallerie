from kavallerie.request import Request, User
from kavallerie.response import Response
from kavallerie.testing import DictSource
from kavallerie.pipes.session import HTTPSession
from kavallerie.pipes.authentication import (
    Authentication, security_bypass, secured, TwoFA)


def test_auth(environ, http_session_store):

    def handler(request):
        return Response(201)

    request = Request(None, environ=environ)
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


def test_filter(environ):

    def handler(request):
        return Response(201)

    def admin_filter(caller, request):
        if request.user.id != 'admin':
            return Response(403)

    authentication = Authentication(
        filters=[admin_filter],
        sources=[
            DictSource({'admin': 'admin'}),
            DictSource({'test': 'test'}),
        ])

    request = Request(None, environ=environ)
    request.user = authentication.authenticator.from_credentials(request, {
        'username': 'admin',
        'password': 'admin'
    })
    response = authentication(handler)(request)
    assert response.status == 201

    request.user = authentication.authenticator.from_credentials(request, {
        'username': 'test',
        'password': 'test'
    })
    response = authentication(handler)(request)
    assert response.status == 403


def test_secured_filter(environ):

    def handler(request):
        return Response(201)

    request = Request(None, environ=environ)
    response = secured('/login')(handler, request)
    assert response.status == 303
    assert response.headers['Location'] == '/login'

    response = secured('/login')(handler, request)
    assert response.status == 303
    assert response.headers['Location'] == '/login'

    user = User()
    user.id = "test"
    request.user = user
    response = secured('/login')(handler, request)
    assert response is None


def test_security_bypass_filter(environ):

    def handler(request):
        return Response(201)

    request = Request(None, environ=environ)
    request.path = '/login'
    response = security_bypass(['/login'])(handler, request)
    assert response.status == 201

    request = Request(None, environ=environ)
    request.path = '/test'
    response = security_bypass('/login')(handler, request)
    assert response is None


def test_twoFA_filter(environ):

    def twofa_checker(request):
        return getattr(request, 'twoFA', False)

    def handler(request):
        return Response(201)

    request = Request(None, environ=environ)
    request.path = '/index'
    response = TwoFA('/sms_qr_code', twofa_checker)(handler, request)
    assert response.status == 303
    assert response.headers['Location'] == '/sms_qr_code'

    request = Request(None, environ=environ)
    request.path = '/sms_qr_code'
    response = TwoFA('/sms_qr_code', twofa_checker)(handler, request)
    assert response.status == 201

    request = Request(None, environ=environ)
    request.twoFA = True
    request.path = '/index'
    response = TwoFA('/sms_qr_code', twofa_checker)(handler, request)
    assert response is None
