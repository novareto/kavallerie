import pytest

from kavallerie.request import Request
from kavallerie.pipes.transaction import Transaction


def test_exception(environ, transaction_manager):

    def handler(request):
        raise NotImplementedError

    manager = transaction_manager()
    request = Request(
        app=None,
        environ=environ,
        utilities={
            'transaction_manager': manager
        }
    )
    middleware = Transaction()(handler)

    with pytest.raises(NotImplementedError):
        middleware(request)

    assert manager.began
    assert manager.aborted
    assert not manager.committed
