import typing as t
import logging
from kavallerie.response import Response
from kavallerie.request import Request
from kavallerie.pipeline import Handler
from kavallerie.access import Filter


class AccessFiltering:

    filters: t.Tuple[Filter, ...]

    def __init__(self, *filters: t.Iterable[Filter]):
        self.filters = tuple(filters)

    def __call__(self,
                 handler: Handler,
                 globalconf: t.Optional[t.Mapping] = None):

        def access_filtering_middleware(request: Request):
            for filter in self.filters:
                if (resp := filter(handler, request)) is not None:
                    return resp

            return handler(request)

        return access_filtering_middleware
