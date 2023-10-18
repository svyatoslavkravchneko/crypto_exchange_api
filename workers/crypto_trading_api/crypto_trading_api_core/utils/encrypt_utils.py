from cryptography.fernet import Fernet
from django.conf import settings


def decrypt_key(encrypted_key):
    f = Fernet(settings.EXCHANGE_ACCOUNT_ENCRYPT_KEY)
    return f.decrypt(encrypted_key.encode('utf-8')).decode('utf-8')