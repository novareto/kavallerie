from webtest import TestApp as WSGIApp
from reiter.application.app import RoutingApplication
from horseman.response import Response


def capitalize(app):
    def capitalize_middleware(config, request):
        response = app(config, request)
        response.body = response.body.upper()
        return response
    return capitalize_middleware


def test_middleware():
    app = RoutingApplication()

    @app.routes.register('/')
    def view(request):
        return Response(200, body='This is my view')

    test = WSGIApp(app)
    response = test.get('/')
    assert response.body == b'This is my view'

    app.middlewares.add(capitalize, order=1)
    response = test.get('/')
    assert response.body == b'THIS IS MY VIEW'
