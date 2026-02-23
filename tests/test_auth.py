from kavallerie.request import Request
from kavallerie.auth import BaseAuthenticator
from kavallerie.testing import DictSource
from kavallerie.meta import User


class UserClass(User):

    def __init__(self, uid: str):
        self.id = uid


forceduser = UserClass("Forced")
testuser = UserClass("Whatever")


def test_no_resolve(environ):

    def preflight(request):
        return testuser

    request = Request(None, environ=environ, user=forceduser)
    authenticator = BaseAuthenticator()

    user = authenticator.identify(request)
    assert user is None


def test_preflight(environ):

    def preflight(request):
        return testuser

    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator(preflights=[preflight])

    user = authenticator.identify(request)
    assert user is testuser

    request = Request(None, environ=environ, user=forceduser)
    user = authenticator.identify(request)
    assert user is testuser


def test_no_source(environ):

    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator()

    user = authenticator.from_credentials(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None


def test_source(environ):

    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator(
        sources={
            "test": DictSource(
                {'admin': 'admin'},
                title="Test",
                description="Test source"
            )
        }
    )

    user = authenticator.from_credentials(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    sourceid, user = authenticator.from_credentials(request, {
        'username': 'admin',
        'password': 'admin'
    })
    assert user.id == 'admin'
    assert sourceid == "test"


def test_several_sources(environ):

    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator(
        sources={
            "test1": DictSource(
                {'admin': 'admin'},
                title="Test 1",
                description="Test source 1"
            ),
            "test2": DictSource(
                {'test': 'test'},
                title="Test 2",
                description="Test source 2"
            ),
            "test3": DictSource(
                {'john': 'doe'},
                title="Test 3",
                description="Test source 3"
            ),
        }
    )

    user = authenticator.from_credentials(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    sourceid, user = authenticator.from_credentials(request, {
        'username': 'test',
        'password': 'test'
    })
    assert user.id == 'test'
    assert sourceid == "test2"
