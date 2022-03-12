def is_bad_response(request, response):
    return response.status >= 400


def transaction(appconfig, app):
    config = appconfig.get('transaction', {})
    veto = config.get('veto', is_bad_response)

    def transaction_middleware(request):
        manager = request.transaction_manager
        txn = manager.begin()
        txn.note(request.path)
        try:
            response = app(request)
            if txn.isDoomed() or (
                    veto is not None and veto(request, response)):
                txn.abort()
            else:
                txn.commit()
            return response
        except Exception as exc:
            txn.abort()
            raise

    return transaction_middleware
