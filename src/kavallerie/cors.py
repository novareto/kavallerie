from typing import Iterable, NamedTuple, Tuple, Iterator
from horseman.types import HTTPMethod
from horseman.response import Headers


class CORSPolicy(NamedTuple):
    origin: str = "*"
    methods: Iterable[HTTPMethod] | None = None
    allow_headers: Iterable[str] | None = None
    expose_headers: Iterable[str] | None = None
    credentials: bool | None = None
    max_age: int | None = None

    def headers(self) -> Headers:
        headers = Headers()
        headers["Access-Control-Allow-Origin"] = self.origin
        if self.methods is not None:
            values = ", ".join(self.methods)
            headers["Access-Control-Allow-Methods"] = values
        if self.allow_headers is not None:
            values = ", ".join(self.allow_headers)
            headers["Access-Control-Allow-Headers"] = values
        if self.expose_headers is not None:
            values = ", ".join(self.expose_headers)
            headers["Access-Control-Expose-Headers"] = values
        if self.max_age is not None:
            headers["Access-Control-Max-Age"] = str(self.max_age)
        if self.credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        return headers

    def preflight(self,
                  origin: str | None = None,
                  acr_method: str | None = None,
                  acr_headers: str | None = None) -> Headers:

        headers = Headers()
        if origin:
            if self.origin == '*':
                headers["Access-Control-Allow-Origin"] = '*'
            elif origin == self.origin:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Vary"] = 'Origin'
            else:
                headers["Access-Control-Allow-Origin"] = self.origin
                headers["Vary"] = 'Origin'

        if self.methods is not None:
            headers["Access-Control-Allow-Methods"] = ", ".join(self.methods)
        elif acr_method:
            headers["Access-Control-Allow-Methods"] = acr_method

        if self.allow_headers is not None:
            values = ", ".join(self.allow_headers)
            headers["Access-Control-Allow-Headers"] = values
        elif acr_headers:
            headers["Access-Control-Allow-Headers"] = acr_headers

        if self.expose_headers is not None:
            values = ", ".join(self.expose_headers)
            headers["Access-Control-Expose-Headers"] = values

        return headers
