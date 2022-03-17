import base64
import hashlib
import secrets


def generate_salt() -> str:
    return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')


class PasswordManager:

    def __init__(self, salt: str = None):
        """if salt is provided, it needs to be a b64 string.
        """
        self.salt = salt or generate_salt()

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
