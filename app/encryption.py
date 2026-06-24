import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


NONCE_SIZE = 12


def encrypt_value(value: str, key: bytes) -> str:
    if value is None:
        return ""
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, value.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_value(token: str, key: bytes) -> str:
    if not token:
        return ""
    raw = base64.b64decode(token.encode("utf-8"))
    nonce = raw[:NONCE_SIZE]
    ciphertext = raw[NONCE_SIZE:]
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
