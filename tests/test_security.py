import base64
from kavallerie.security import PasswordManager


def test_password_generation():
    b64_expected_value = "/bVkHA4G/VOskjaCgNYyTz1BhgD+9X8bxCNEPGGpnDCJbWHDXIW0G8IlSBhDdJsXTjrXt/7yQguBwJ3sxSmSKA=="
    b64_salt = "lZtleWv1DeEcNIr8MTzdeg=="

    pwm = PasswordManager(salt=b64_salt)
    assert pwm.salt == b64_salt
    assert pwm.create('test') == b64_expected_value
