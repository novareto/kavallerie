import pytest
from horseman.exceptions import HTTPError
from kavallerie.app import RoutingApplication
from kavallerie.response import Response


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
