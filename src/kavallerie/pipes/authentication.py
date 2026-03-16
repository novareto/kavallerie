import typing as t
import logging
from kavallerie.request import Request
from kavallerie.auth import BaseAuthenticator
from kavallerie.pipeline import Handler
from authsources.identity import User


logger = logging.getLogger(__name__)


U = t.TypeVar("U", bound=User)


class Authentication(t.Generic[U]):

    authenticator: BaseAuthenticator
    wrapper: t.Callable[[User, Request], U] | None = None

    def __init__(self,
                 authenticator: BaseAuthenticator, *,
                 wrapper: t.Callable[[User, Request], U] | None = None):
        self.authenticator = authenticator
        self.wrapper = wrapper

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Mapping | None = None):

        def authentication_middleware(request):
            request.utilities['authentication'] = self.authenticator

            if request.user is not None:
                logger.info(f'Request contains a user: {request.user}. '
                            'Skipping authentication.')

            else:
                user = self.authenticator.identify(request)
                if user is not None and self.wrapper is not None:
                    logger.info(f'User found. Wrapping.')
                    user = self.wrapper(user, request)
                request.user = user

            if request.user is None:
                logger.info(f'No user found by authentication.')

            response = handler(request)
            del request.utilities['authentication']
            return response

        return authentication_middleware
