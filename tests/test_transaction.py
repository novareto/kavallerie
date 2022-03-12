from transaction import TransactionManager
from transaction.interfaces import TransientError
from kavallerie.transaction import transaction
from kavallerie.request import Request
from webtest import TestApp as Client
import pytest


class DummyTransactionManager(TransactionManager):
    _resources = []

    def __init__(self, doomed=False, retryable=False):
        self.doomed = doomed
        self.began = 0
        self.committed = 0
        self.aborted = 0
        self.active = False

    def get(self):
        return self

    def isDoomed(self):
        return self.doomed

    def begin(self):
        self.began += 1
        self.active = True
        return self

    def commit(self):
        self.committed += 1

    def abort(self):
        self.active = False
        self.aborted += 1

    def note(self, value):
        self._note = value


def test_exception():

    def handler(request):
        raise NotImplementedError

    manager = DummyTransactionManager()
    def factory():
        return manager

    request = Request('/', app=None, environ={
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': ''
    })
    middleware = transaction({}, handler, transaction_factory=factory)

    with pytest.raises(NotImplementedError):
        middleware(request)

    assert manager.began
    assert manager.aborted
    assert not manager.committed
