from typing import List, Callable
from kavallerie.pipes.authentication import Filter
from kavallerie.response import Response
from kavallerie.request import Request


def security_bypass(urls: List[str]) -> Filter:
    unprotected = frozenset(urls)
    def _filter(caller, request):
        if request.path in unprotected:
            return caller(request)
    return _filter


def secured(path: str) -> Filter:
    def _filter(caller, request):
        if request.user is None:
            return Response.redirect(request.script_name + path)
    return _filter


def TwoFA(path: str, checker: Callable[[Request], bool]) -> Filter:
    def _filter(caller, request):
        if request.path == path:
            return caller(request)
        if not checker(request):
            return Response.redirect(request.script_name + path)
    return _filter
