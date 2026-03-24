import logging
from kavallerie.pipeline import Handler
from kavallerie.response import Response, Headers


Logger = logging.getLogger(__name__)


def CORS(handler: Handler):
    def cors_policy_handler(request):
        if request.cors_policy is None or request.method != 'OPTIONS':
            return handler(request)

        # We intercept the preflight.
        # If a route was possible registered for OPTIONS,
        # this will override it.
        Logger.debug('Cors policy found: crafting preflight response.')
        origin = request.get('ORIGIN')
        acr_method = request.get('ACCESS_CONTROL_REQUEST_METHOD')
        acr_headers = request.get('ACCESS_CONTROL_REQUEST_HEADERS')
        headers = request.cors_policy.preflight(
            origin=origin,
            acr_method=acr_method,
            acr_headers=acr_headers
        )
        return Response(200, headers=headers)

    return cors_policy_handler
