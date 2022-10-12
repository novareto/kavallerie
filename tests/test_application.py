import pytest
from horseman.http import HTTPError
from kavallerie.app import RoutingApplication
from kavallerie.response import Response


def test_application_path_handling(environ):
    application = RoutingApplication()

    @application.routes.register('/')
    def handler(request):
        return Response(200)

    response = application.resolve('/', environ)
    assert response.status == 200

    response = application.resolve('', environ)
    assert response.status == 200

    with pytest.raises(HTTPError):
        application.resolve('/test', environ)
