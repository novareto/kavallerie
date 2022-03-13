import pytest
from copy import deepcopy
from http_session.meta import Store
from unittest.mock import Mock
from transaction import TransactionManager
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


class SessionMemoryStore(Store):

    def __init__(self, TTL=None):
        self.data = {}
        self.touch = Mock()
        self.TTL = TTL

    def __iter__(self):
        return iter(self.data.keys())

    def get(self, sid):
        """We return a copy, to avoid mutability by reference.
        """
        data = self.data.get(sid)
        if data is not None:
            return deepcopy(data)
        return data

    def set(self, sid, session):
        self.data[sid] = session

    def clear(self, sid):
        if sid in self.data:
            self.data[sid].clear()

    def delete(self, sid):
        del self.data[sid]


@pytest.fixture
def transaction_manager():
    return DummyTransactionManager


@pytest.fixture
def http_session_store():
    return SessionMemoryStore
