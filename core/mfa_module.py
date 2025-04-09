import pyotp

# Static test user (you can expand this later)
users = {
    "admin": {
        "totp_secret": "JBSWY3DPEHPK3PXP"  # this is "Hello!" base32 encoded
    }
}

def get_totp_uri(username):
    user = users.get(username)
    if not user:
        return None
    return pyotp.totp.TOTP(user["totp_secret"])

def validate_otp(username, otp_input):
    totp = get_totp_uri(username)
    if not totp:
        return False
    return totp.verify(otp_input)

