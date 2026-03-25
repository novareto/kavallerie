import pytest
from horseman.exceptions import HTTPError
from kavallerie.app import RoutingApplication
from kavallerie.response import Response
from webtest import TestApp as WebApp


def test_application_path_handling(environ):
    application = RoutingApplication()

    @application.routes.register('/')
    def handler(request):
        return Response(200)

    response = application.resolve({**environ, 'PATH_INFO': '/'})
    assert response.status == 200

    response = application.resolve({**environ, 'PATH_INFO': ''})
    assert response.status == 200

    with pytest.raises(HTTPError):
        application.resolve({**environ, 'PATH_INFO': '/test'})


def test_application_exception_handling(environ):
    application = RoutingApplication()

    @application.routes.register('/')
    def handler(request):
        raise HTTPError(400, body="This is an error")

    app = WebApp(application)
    response = app.get('/', expect_errors=True)
    assert response.status == '400 Bad Request'
    assert response.body == b'This is an error'
