import abc
import base64
import hashlib
import hmac
import pyotp
import secrets
from typing import Any, List, Callable, Union
from horseman.types import Environ
from kavallerie.pipes.authentication import Filter
from kavallerie.response import Response
from kavallerie.request import Request, User
from kavallerie.utils import unique


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


class PasswordManager:

    __slots__ = ('salt',)

    def __init__(self, salt: str = None):
        """if salt is provided, it needs to be a b64 string.
        """
        self.salt = salt or self.generate_salt()

    @staticmethod
    def generate_salt() -> str:
        return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')

    def create(self, word: str) -> str:
        token = hashlib.pbkdf2_hmac(
            'sha256',
            word.encode('utf-8'),
            base64.b64decode(self.salt),
            27500,  # iterations
            dklen=64
        )
        return base64.b64encode(token).decode('utf-8')

    def verify(self, word: str, challenger: str) -> bool:
        token = self.create(word)
        if token == challenger:
            return True
        return False


class TOTP:

    def __init__(self, user: User):
        self.user = user

    @unique
    def shared_key(self) -> bytes:
        key = hashlib.sha256(str(self.user.id).encode("utf-8"))
        return base64.b32encode(key.digest())

    @unique
    def TOTP(self) -> bytes:
        """We use mostly default values for Google Authenticator compat.
        """
        return pyotp.TOTP(
            self.shared_key,
            name=str(self.user.id),
        )

    @unique
    def OTP_URI(self) -> str:
        return self.TOTP.provisioning_uri()

    def generate_token(
            self, digits=8, digest=hashlib.sha256, interval=60*60):  # 1h
        return pyotp.TOTP(
            self.shared_key,
            name=str(self.user.id),
            digits=digits,
            digest=digest,
            interval=interval
        )
