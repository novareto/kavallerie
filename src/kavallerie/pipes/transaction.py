import typing as t
from transaction import TransactionManager
from kavallerie.pipeline import Handler, MiddlewareFactory
from kavallerie.request import Request
from kavallerie.response import Response


class Transaction(MiddlewareFactory):

    class Configuration(t.NamedTuple):
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
            try:
                response = handler(request)
                if txn.isDoomed() or (
                        isinstance(response, Response)
                        and response.status >= 400):
                    txn.abort()
                else:
                    txn.commit()
                return response
            except Exception:
                txn.abort()
                raise

        return transaction_middleware
