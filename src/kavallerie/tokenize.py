import base64
import hashlib
import pyotp
from kavallerie.request import User
from kavallerie.utils import unique


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
