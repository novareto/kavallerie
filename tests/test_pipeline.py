import pytest
from webtest import TestApp as WSGIApp
from kavallerie.response import Response
from kavallerie.request import Request
from kavallerie.app import RoutingApplication
from kavallerie.pipeline import Pipeline


def handler(request):
    return Response(200, body='This is my view')


def capitalize(app, config=None):
    def capitalize_middleware(request):
        response = app(request)
        response.body = response.body.upper()
        return response
    return capitalize_middleware


def suffix(app, config):
    def suffix_middleware(request):
        response = app(request)
        response.body += ' my suffix'
        return response
    return suffix_middleware


def test_middleware():
    app = RoutingApplication()

    @app.routes.register('/')
    def view(request):
        return Response(200, body='This is my view')

    test = WSGIApp(app)
    response = test.get('/')
    assert response.body == b'This is my view'

    app.pipeline.add(capitalize, order=1)
    response = test.get('/')
    assert response.body == b'THIS IS MY VIEW'


def test_pipeline(environ):
    pipeline = Pipeline()
    assert list(pipeline) == []

    pipeline.add(capitalize, order=1)
    assert list(pipeline) == [(1, capitalize)]

    with pytest.raises(KeyError):
        pipeline.add(capitalize, order=1)

    assert list(pipeline) == [(1, capitalize)]

    pipeline.add(suffix)
    assert list(pipeline) == [
        (0, suffix),
        (1, capitalize)
    ]

    request = Request(None, environ=environ)
    response = pipeline.wrap(handler)(request)
    assert response.body == 'THIS IS MY VIEW my suffix'


def test_pipeline_add_remove():
    pipeline = Pipeline()
    pipeline.add(capitalize, order=1)
    assert list(pipeline) == [(1, capitalize)]
    pipeline.remove(capitalize, order=1)
    assert list(pipeline) == []

    with pytest.raises(KeyError):
        pipeline.remove(capitalize, order=1)
