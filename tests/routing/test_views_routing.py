import hamcrest
import pytest
from kavallerie.meta import APIView
from kavallerie.routing import get_endpoints
from plum import NotFoundLookupError


def view_func(request):
    pass


class SomeCallable:

    def __call__(self, request):
        pass


class View(APIView):

    def GET(request):
        pass

    def HEAD(request):
        pass

    def POST(request):
        pass

    def something_else(self):
        pass


def test_simple_class_payload():
    payload = list(get_endpoints(SomeCallable))

    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__)),
                {'GET',}
            ),
        )
    )

    payload = list(get_endpoints(SomeCallable, methods=['POST']))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__)),
                {'POST'}
            ),
        )
    )

    payload = list(get_endpoints(SomeCallable, methods=['DELETE', 'POST']))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(SomeCallable.__call__)),
                {'DELETE', 'POST'}
            ),
        )
    )


def test_simple_instance_payload():
    inst = SomeCallable()

    with pytest.raises(NotFoundLookupError) as exc:
        list(get_endpoints(inst))


def test_view_class_payload():
    payload = list(get_endpoints(View))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(View.GET)),
                {'GET'},
            ),
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(View.HEAD)),
                {'HEAD'}
            ),
            hamcrest.contains_exactly(
                hamcrest.has_property(
                    '__func__', hamcrest.is_(View.POST)),
                {'POST'}
            ),
        )
    )

    with pytest.raises(AttributeError) as exc:
        list(get_endpoints(View, methods=['POST']))

    assert str(exc.value) == (
        'Registration of APIView does not accept methods.')


def test_view_instance_payload():
    inst = View()
    payload = list(get_endpoints(inst))
    hamcrest.assert_that(
        payload, hamcrest.contains_exactly(
            (inst.GET, {'GET'}),
            (inst.HEAD, {'HEAD'}),
            (inst.POST, {'POST'})
        )
    )

    with pytest.raises(AttributeError) as exc:
        list(get_endpoints(inst, methods=['POST']))

    assert str(exc.value) == (
        'Registration of APIView does not accept methods.')
