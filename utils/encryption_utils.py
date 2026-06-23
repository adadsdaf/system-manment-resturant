import hashlib
import os
import base64
import secrets
from datetime import datetime


def sha256_hash(data: str, salt: str = '') -> str:
    combined = (data + salt).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()


def generate_license_key(prefix: str = 'ITQAN', length: int = 16) -> str:
    rand = secrets.token_hex(length // 2).upper()
    parts = [rand[i:i+4] for i in range(0, len(rand), 4)]
    year = datetime.now().year
    return f"{prefix}-{year}-{'-'.join(parts[:3])}"


def generate_device_token() -> str:
    return secrets.token_urlsafe(32)


def mask_fingerprint(fingerprint: str) -> str:
    if not fingerprint or len(fingerprint) < 8:
        return fingerprint
    return fingerprint[:6] + '****' + fingerprint[-6:]


def generate_salt() -> str:
    return secrets.token_hex(16)


def verify_hash(data: str, hashed: str, salt: str = '') -> bool:
    return sha256_hash(data, salt) == hashed
