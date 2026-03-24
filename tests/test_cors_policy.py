import pytest
from kavallerie.cors import CORSPolicy


def test_policy():
    cors1 = CORSPolicy()
    cors2 = CORSPolicy()
    assert cors1 == cors2
    assert not cors1 is cors2

    cors1 = CORSPolicy(
        methods=['GET', 'POST'],
        allow_headers=['Accept-Encoding'],
        expose_headers=['Accept-Encoding'],
        max_age=36000
    )
    assert cors1 != cors2

    cors2 = CORSPolicy(
        methods=['GET', 'POST'],
        allow_headers=['Accept-Encoding'],
        expose_headers=['Accept-Encoding'],
        max_age=36000
    )
    assert cors1 == cors2

    cors2 = CORSPolicy(
        methods=['GET', 'POST'],
        allow_headers=['Accept-Encoding'],
        expose_headers=['Accept-Encoding'],
        max_age=19000
    )
    assert cors1 != cors2

    cors2 = CORSPolicy(
        methods=['GET', 'POST'],
        allow_headers=[],
        expose_headers=['Accept-Encoding'],
        max_age=36000
    )
    assert cors1 != cors2


def test_empty_policy():

    cors = CORSPolicy()
    assert cors.origin == '*'
    assert cors.methods is None
    assert cors.allow_headers is None
    assert cors.expose_headers is None
    assert cors.credentials is None
    assert cors.max_age is None

    with pytest.raises(AttributeError):
        cors.origin = 'new origin'

    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*')
    ]


def test_policy_headers():
    cors = CORSPolicy(
        allow_headers=['X-Custom-Header', 'Accept-Encoding'],
    )
    assert cors.allow_headers == ['X-Custom-Header', 'Accept-Encoding']
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'X-Custom-Header, Accept-Encoding')
    ]

    cors = CORSPolicy(
        allow_headers=['X-Custom-Header', 'Accept-Encoding'],
        expose_headers=['Content-Type'],
    )
    assert cors.allow_headers == ['X-Custom-Header', 'Accept-Encoding']
    assert cors.expose_headers == ['Content-Type']
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'X-Custom-Header, Accept-Encoding'),
        ('Access-Control-Expose-Headers', 'Content-Type'),
    ]


def test_policy_methods():
    cors = CORSPolicy(
        methods=['GET', 'POST'],
    )
    assert cors.methods == ['GET', 'POST']
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST')
    ]


def test_policy_origin():
    cors = CORSPolicy(
        origin='http://example.com'
    )
    assert cors.origin == 'http://example.com'
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', 'http://example.com'),
    ]


def test_policy_max_age():
    cors = CORSPolicy(
        max_age=36000
    )
    assert cors.max_age == 36000
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Max-Age', '36000')
    ]


def test_policy_credentials():
    cors = CORSPolicy(
        credentials=True
    )
    assert cors.credentials is True
    headers = cors.headers()
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Credentials', 'true'),
    ]


def test_policy_headers_preflight():

    cors = CORSPolicy()
    headers = cors.preflight(
        acr_headers='X-Custom-Header, Accept-Encoding'
    )
    assert list(headers.items()) == [
        ('Access-Control-Allow-Headers', 'X-Custom-Header, Accept-Encoding')
    ]

    cors = CORSPolicy(
        allow_headers=['X-Custom-Header']
    )
    headers = cors.preflight(
        acr_headers='X-Custom-Header, Accept-Encoding'
    )
    assert list(headers.items()) == [
        ('Access-Control-Allow-Headers', 'X-Custom-Header')
    ]

    cors = CORSPolicy(
        allow_headers=['X-Custom-Header', 'Accept-Encoding'],
        expose_headers=['Accept-Encoding']
    )
    headers = cors.preflight(
        acr_headers='X-Custom-Header, Accept-Encoding'
    )
    assert list(headers.items()) == [
        ('Access-Control-Allow-Headers', 'X-Custom-Header, Accept-Encoding'),
        ('Access-Control-Expose-Headers', 'Accept-Encoding')
    ]

    cors = CORSPolicy(
        expose_headers=['Accept-Encoding']
    )
    headers = cors.preflight(
        acr_headers='X-Custom-Header, Accept-Encoding'
    )
    assert list(headers.items()) == [
        ('Access-Control-Allow-Headers', 'X-Custom-Header, Accept-Encoding'),
        ('Access-Control-Expose-Headers', 'Accept-Encoding')
    ]


def test_policy_method_preflight():

    cors = CORSPolicy()
    headers = cors.preflight(acr_method='POST')
    assert list(headers.items()) == [
        ('Access-Control-Allow-Methods', 'POST')
    ]

    cors = CORSPolicy(methods=['GET', 'POST'])
    headers = cors.preflight(acr_method='POST')
    assert list(headers.items()) == [
        ('Access-Control-Allow-Methods', 'GET, POST')
    ]


def test_policy_origin_preflight():

    cors = CORSPolicy()
    assert list(cors.preflight()) == []
    headers = cors.preflight(origin='*')
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', '*')
    ]

    cors = CORSPolicy(origin='http://example.com')

    headers = cors.preflight(origin='*')
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', 'http://example.com'),
        ('Vary', 'Origin')
    ]

    headers = cors.preflight(origin='http://example.com')
    assert list(headers.items()) == [
        ('Access-Control-Allow-Origin', 'http://example.com'),
        ('Vary', 'Origin')
    ]
