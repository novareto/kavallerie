from kavallerie.request import Request
from kavallerie.auth import BaseAuthenticator
from authsources.abc.identity import User
from authsources.abc.source import Source
from authsources.abc.actions import Preflight
from authsources.sources.mapping import DictSource


class UserClass(User):

    def __init__(self, uid: str):
        self.id = uid


forceduser = UserClass("Forced")
testuser = UserClass("Whatever")


class FakePreflight(Preflight):

    def preflight(self):
        return testuser


class FakeSource(Source):
    title: str = "Fake"
    description: str = "Fake source for testing purposes."
    actions = {
        Preflight: FakePreflight
    }


def test_no_resolve(environ):

    request = Request(None, environ=environ, user=forceduser)
    authenticator = BaseAuthenticator()

    user = authenticator.identify(request)
    assert user is None


def test_preflight(environ):
    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator(sources={"fake": FakeSource()})

    user = authenticator.identify(request)
    assert user is testuser

    request = Request(None, environ=environ, user=forceduser)
    user = authenticator.identify(request)
    assert user is testuser


def test_no_source(environ):

    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator()

    sourceid, user = authenticator.challenge(request, {
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

    sourceid, user = authenticator.challenge(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    sourceid, user = authenticator.challenge(request, {
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

    sourceid, user = authenticator.challenge(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    sourceid, user = authenticator.challenge(request, {
        'username': 'test',
        'password': 'test'
    })
    assert user.id == 'test'
    assert sourceid == "test2"
