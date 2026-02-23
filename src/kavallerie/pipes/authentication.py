import typing as t
import logging
from kavallerie.request import Request
from kavallerie.auth import BaseAuthenticator
from kavallerie.pipeline import Handler


logger = logging.getLogger(__name__)


class Authentication:

    def __init__(self, authenticator: BaseAuthenticator):
        self.authenticator = authenticator

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Mapping | None = None):

        def authentication_middleware(request):
            request.utilities['authentication'] = self.authenticator

            if request.user is not None:
                logger.info(f'Request contains a user: {request.user}. '
                            'Skipping authentication.')

            else:
                request.user = self.authenticator.identify(request)

            if request.user is None:
                logger.info(f'No user found by authentication.')

            response = handler(request)
            del request.utilities['authentication']
            return response

        return authentication_middleware
