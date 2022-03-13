import typing as t
from transaction import TransactionManager
from kavallerie.pipeline import Handler, MiddlewareFactory
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

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def transaction_middleware(request):
            manager = request.utilities.get('transaction_manager')
            if manager is None:
                manager = self.config.factory()
                request.utilities['transaction_manager'] = manager

            txn = manager.begin()
            txn.note(request.path)
            try:
                response = handler(request)
                if txn.isDoomed() or self.config.veto(request, response):
                    txn.abort()
                else:
                    txn.commit()
                return response
            except Exception:
                txn.abort()
                raise

        return transaction_middleware
