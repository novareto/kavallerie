from kavallerie.request import Request
from kavallerie.auth import Authenticator
from kavallerie.testing import DictSource


def test_source(environ):

    request = Request('/', app=None, environ=environ)
    authenticator = Authenticator(
        'user', [
            DictSource({'admin': 'admin'}),
        ]
    )

    user = authenticator.from_credentials(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    user = authenticator.from_credentials(request, {
        'username': 'admin',
        'password': 'admin'
    })
    assert user.id == 'admin'


def test_several_sources(environ):

    request = Request('/', app=None, environ=environ)
    authenticator = Authenticator(
        'user', [
            DictSource({'admin': 'admin'}),
            DictSource({'test': 'test'}),
            DictSource({'john': 'doe'}),
        ]
    )

    user = authenticator.from_credentials(request, {
        'username': 'john',
        'password': 'test'
    })
    assert user is None

    user = authenticator.from_credentials(request, {
        'username': 'test',
        'password': 'test'
    })
    assert user.id == 'test'
