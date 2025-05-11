# accounts/utils.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def generate_password_reset_token(user):
    return signer.sign(user.pk)

def verify_password_reset_token(token, max_age=3600):  # 1時間以内有効
    try:
        unsigned = signer.unsign(token, max_age=max_age)
        return unsigned
    except (BadSignature, SignatureExpired):
        return None
