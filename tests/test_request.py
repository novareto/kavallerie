from kavallerie.request import Request


def test_request(environ):
    request = Request(None, environ=environ)
    assert request.utilities == {}
    assert request.path == '/'
    assert request.method == 'GET'
    assert request.route is None
    assert request.cors_policy is None
    assert request.query == {}
    assert request.cookies == {}
    assert request.content_type is None
    assert request.application_uri == "http://test_domain.com"
    assert request.uri() == "http://test_domain.com/"
    assert request.uri(include_query=False) == "http://test_domain.com/"


def test_request_uri(environ):
    environ = {**environ, 'QUERY_STRING': 'foo=bar'}
    request = Request(None, environ=environ)
    assert request.uri(include_query=False) == "http://test_domain.com/"
    assert request.uri(include_query=True) == (
        "http://test_domain.com/?foo%3Dbar"
    )

    environ = {**environ}
    del environ['QUERY_STRING']
    request = Request(None, environ=environ)
    assert request.uri(include_query=False) == "http://test_domain.com/"
    assert request.uri(include_query=True) == "http://test_domain.com/"
