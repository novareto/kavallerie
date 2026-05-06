from autorouting import Route
from kavallerie.routing import Router


def test_merge_method_registration_operation():
    router1 = Router()
    router2 = Router()

    @router1.register('/test')
    def my_get(request):
        pass

    @router2.register('/test', methods=['POST'])
    def my_post(request):
        pass

    assert list(router1) == [
        ('/test', 'GET', Route(routed=my_get, requirements={})),
    ]

    assert list(router2) == [
        ('/test', 'POST', Route(routed=my_post, requirements={})),
    ]

    router3 = router1 | router2
    assert list(router3) == [
        ('/test', 'GET', Route(routed=my_get, requirements={})),
        ('/test', 'POST', Route(routed=my_post, requirements={})),
    ]


def test_override_method_registration_operation():
    router1 = Router()
    router2 = Router()

    @router1.register('/test')
    def my_get(request):
        pass

    @router2.register('/test', methods=['GET'])
    def my_other_get(request):
        pass

    assert list(router1) == [
        ('/test', 'GET', Route(routed=my_get, requirements={})),
    ]

    assert list(router2) == [
        ('/test', 'GET', Route(routed=my_other_get, requirements={})),
    ]

    router3 = router1 | router2
    assert list(router3) == [
        ('/test', 'GET', Route(routed=my_get, requirements={})),
        ('/test', 'GET', Route(routed=my_other_get, requirements={})),
    ]

    router3 = router2 | router1
    assert list(router3) == [
        ('/test', 'GET', Route(routed=my_other_get, requirements={})),
        ('/test', 'GET', Route(routed=my_get, requirements={})),
    ]
