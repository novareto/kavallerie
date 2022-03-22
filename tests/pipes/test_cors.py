from roughrider.cors.policy import CORSPolicy
from kavallerie.request import Request
from kavallerie.response import Response
from kavallerie.pipes.cors import CORS


def test_preflight(environ):

    def handler(request):
        return Response(204)

    policy = CORSPolicy(
        origin='http://example.com',
        allow_headers=['X-Custom-Header', 'Accept-Encoding'],
        expose_headers=['Accept-Encoding']
    )

    # Normal request, pass through
    request = Request('/', app=None, environ=environ, cors_policy=policy)
    response = CORS(handler)(request)
    assert response.status == 204

    # Preflight request
    opts_env = {
        **environ,
        'REQUEST_METHOD': 'OPTIONS'
    }
    request = Request('/', app=None, environ=opts_env, cors_policy=policy)
    response = CORS(handler)(request)
    assert response.status == 200
    assert dict(response.headers.coalesced_items()) == {
        'Access-Control-Expose-Headers': 'Accept-Encoding',
        'Access-Control-Allow-Headers': 'X-Custom-Header, Accept-Encoding'
    }

    # Preflight request with origin
    opts_env = {
        **environ,
        'REQUEST_METHOD': 'OPTIONS',
        'ORIGIN': '*'
    }
    request = Request('/', app=None, environ=opts_env, cors_policy=policy)
    response = CORS(handler)(request)
    assert response.status == 200
    assert dict(response.headers.coalesced_items()) == {
        'Vary': 'Origin',
        'Access-Control-Allow-Origin': 'http://example.com',
        'Access-Control-Expose-Headers': 'Accept-Encoding',
        'Access-Control-Allow-Headers': 'X-Custom-Header, Accept-Encoding'
    }
