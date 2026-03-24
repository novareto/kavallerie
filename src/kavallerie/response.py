import orjson
from http import HTTPStatus
from typing import Iterable, Any
from horseman.response import Response as BaseResponse, Headers
from horseman.types import Environ, HTTPCode, StartResponse


REDIRECT = frozenset((
    HTTPStatus.MULTIPLE_CHOICES,
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
    HTTPStatus.NOT_MODIFIED,
    HTTPStatus.USE_PROXY,
    HTTPStatus.TEMPORARY_REDIRECT,
    HTTPStatus.PERMANENT_REDIRECT
))


class Response(BaseResponse):

    @classmethod
    def redirect(cls, location, code: HTTPCode = 303,
                 body: Iterable | None = None,
                 headers: Headers | None = None):
        if code not in REDIRECT:
            raise ValueError(f"{code}: unknown redirection code.")
        if not headers:
            headers = {'Location': location}
        else:
            headers['Location'] = location
        return cls(code, body, headers)

    @classmethod
    def from_file_iterator(cls, filename: str, body: Iterable[bytes],
                           headers: Headers | None = None):
        if headers is None:
            headers = {
                "Content-Disposition": f"attachment;filename={filename}"}
        elif "Content-Disposition" not in headers:
            headers["Content-Disposition"] = (
                f"attachment;filename={filename}")
        return cls(200, body, headers)

    @classmethod
    def to_json(cls, code: HTTPCode = 200, body: Any | None = None,
                headers: Headers | None = None):
        data = orjson.dumps(body)
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, data, headers)

    @classmethod
    def from_json(cls, code: HTTPCode = 200, body: str = '',
                  headers: Headers | None = None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, body, headers)

    @classmethod
    def html(cls, code: HTTPCode = 200, body: str = '',
             headers: Headers | None = None):
        if headers is None:
            headers = {'Content-Type': 'text/html; charset=utf-8'}
        else:
            headers['Content-Type'] = 'text/html; charset=utf-8'
        return cls(code, body, headers)
