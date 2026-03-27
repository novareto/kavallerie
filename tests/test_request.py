from kavallerie.request import Request


def test_request(environ):
    request = Request(None, environ=environ)
    assert request.utilities == {}
    assert request.path == '/'
    assert request.app is None
    assert request.method == 'GET'
    assert request.route is None
    assert request.cors_policy is None
    assert request.query == {}
    assert request.cookies == {}
    assert request.content_type == ''
    assert request.application_uri == "http://test_domain.com"
    assert request.uri() == "http://test_domain.com/"
    assert request.uri(include_query=False) == "http://test_domain.com/"
    assert request.headers is request._environ


def test_request_flags(environ):
    request = Request(None, environ=environ)
    assert request.flags.whatever is None
    assert request.flags.something_else is None
    request.flags.whatever = True
    assert request.flags.whatever is True
    assert request.flags.something_else is None
    request.flags.something_else = "non bool value"
    assert request.flags.something_else == "non bool value"
