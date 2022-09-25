import typing as t
from horseman.http import HTTPError
from kavallerie.request import Request
from kavallerie.response import Response


HTTPErrorCatcher = t.Callable[[Exception, Request], t.Optional[Response]]


class HTTPErrorCatchers(t.Dict[int, HTTPErrorCatcher]):

    def __call__(self, handler, conf):
        def error_handler(request):
            try:
                response = handler(request)
            except HTTPError as exc:
                catcher = self.get(exc.status)
                if catcher is None:
                    raise exc
                response = catcher(exc, request)
                if response is None:
                    raise exc
            return response
        return error_handler
