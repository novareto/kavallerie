import http
import webtest
import pytest
import horseman.response

from kavallerie.errors import HTTPError


def test_resolve(node):

    @node.routes.register('/getter', methods=['GET'])
    def fake_route(request):
        return horseman.response.Response(200, body=b'OK !')

    node.routes.finalize()
    result = node.resolve({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/getter'})
    assert isinstance(result, horseman.response.Response)

    with pytest.raises(HTTPError) as exc:
        node.resolve({'REQUEST_METHOD': 'POST', 'PATH_INFO': '/getter'})

    assert exc.value.status == http.HTTPStatus(404)


def test_wsgi_roundtrip(node):

    app = webtest.TestApp(node)
    response = app.get('/getter', status=404)
    assert response.body == b'Nothing matches the given URI'

    @node.routes.register('/getter', methods=['GET'])
    def fake_route(request):
        return horseman.response.Response(200, body=b'OK !')

    node.routes.finalize()
    response = app.get('/getter')
    assert response.body == b'OK !'

    response = app.post('/getter', status=404)
    assert response.status == '404 Not Found'
