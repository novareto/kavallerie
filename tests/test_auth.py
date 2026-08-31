from authsources.identity import User
from kavallerie.auth import ResolvedUser
from kavallerie.request import Request
from kavallerie.response import Response
from authsources.sources.mapping import DictSource, Fetch
from kavallerie.auth import BaseAuthenticator


def test_authenticator_fetch(environ):
    request = Request(None, environ=environ)
    authenticator = BaseAuthenticator(
        sources={
            "test": DictSource(
                {
                    'admin': {
                        "password": 'admin'
                    }
                },
                title="Test",
                description="Test source",
                actions=[Fetch]
            )
        }
    )
    user = authenticator.fetch(request, 'admin')
    assert user is not None
    assert isinstance(user, ResolvedUser)
    assert user.source_id == "test"
    assert user.data == {'password': 'admin'}

    user = authenticator.fetch(request, 'unknown')
    assert user is None
