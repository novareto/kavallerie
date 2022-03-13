import typing as t
from transaction import TransactionManager
from kavallerie.pipeline import MiddlewareFactory
from kavallerie.request import Request
from kavallerie.response import Response


def is_bad_response(request, response):
    return response.status >= 400


class Transaction(MiddlewareFactory):

    id = 'transaction_manager'

    class Configuration(t.NamedTuple):
        veto: t.Callable[[Request, Response], bool] = is_bad_response
        factory: t.Callable[[], TransactionManager] = (
            lambda: TransactionManager(explicit=True)
        )

    def __call__(self, app, globalconf):
        def transaction_middleware(request):
            manager = request.utilities.get('transaction_manager')
            if manager is None:
                manager = self.config.factory()
                request.utilities['transaction_manager'] = manager

            txn = manager.begin()
            txn.note(request.path)
            try:
                response = app(request)
                if txn.isDoomed() or self.config.veto(request, response):
                    txn.abort()
                else:
                    txn.commit()
                return response
            except Exception as exc:
                txn.abort()
                raise

        return transaction_middleware
