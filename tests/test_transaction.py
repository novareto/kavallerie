import pytest

from kavallerie.request import Request
from kavallerie.pipes.transaction import Transaction


def test_exception(transaction_manager):

    def handler(request):
        raise NotImplementedError

    manager = transaction_manager()
    request = Request(
        '/', app=None,
        utilities={
            'transaction_manager': manager
        },
        environ={
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': ''
        }
    )
    middleware = Transaction()(handler)

    with pytest.raises(NotImplementedError):
        middleware(request)

    assert manager.began
    assert manager.aborted
    assert not manager.committed
