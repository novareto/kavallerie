import typing as t
import logging
from pathlib import PurePosixPath
from kavallerie.response import Response
from kavallerie.request import Request
from kavallerie.pipeline import Handler


Filter = t.Callable[[Handler, Request], Response | None]


def security_bypass(urls: t.Iterable[str]) -> Filter:
    unprotected = frozenset(
        PurePosixPath(bypass) for bypass in urls
    )
    def _filter(caller, request):
        path = PurePosixPath(request.path)
        for bypass in unprotected:
            if path.is_relative_to(bypass):
                return caller(request)

    return _filter


def secured(path: str) -> Filter:

    def _filter(caller, request):
        if request.user is None:
            return Response.redirect(request.script_name + path)

    return _filter


def TwoFA(path: str, checker: t.Callable[[Request], bool]) -> Filter:

    def _filter(caller, request):
        if request.path == path:
            return caller(request)
        if not checker(request):
            return Response.redirect(request.script_name + path)

    return _filter
