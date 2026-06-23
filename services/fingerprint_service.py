import hashlib
import uuid
import platform
import socket


def generate_server_fingerprint() -> str:
    parts = []
    try:
        parts.append(platform.node())
    except Exception:
        pass
    try:
        parts.append(socket.gethostname())
    except Exception:
        pass
    try:
        parts.append(str(uuid.getnode()))
    except Exception:
        pass
    try:
        parts.append(platform.machine())
        parts.append(platform.processor())
    except Exception:
        pass

    raw = '|'.join(filter(None, parts))
    if not raw:
        raw = str(uuid.uuid4())
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def generate_web_fingerprint(ip_address: str, user_agent: str, extra: str = '') -> str:
    salt = 'ITQAN_LICENSE_SALT_2025'
    raw = f"{ip_address}|{user_agent}|{extra}|{salt}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def generate_client_fingerprint(components: dict) -> str:
    keys = sorted(components.keys())
    parts = [f"{k}={components[k]}" for k in keys if components.get(k)]
    raw = '|'.join(parts) + '|ITQAN_2025'
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()
