import time
from functools import wraps
from threading import Lock

from flask import abort, request


_LIMIT_STORE: dict[tuple[str, str], list[float]] = {}
_LIMIT_LOCK = Lock()
_LAST_CLEANUP = 0.0
_CLEANUP_INTERVAL_SECONDS = 120


def get_client_ip() -> str:
    return request.remote_addr or "unknown"


def rate_limit(key: str, max_calls: int, period_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            global _LAST_CLEANUP
            remote = get_client_ip()
            now = time.time()
            index = (key, remote)

            with _LIMIT_LOCK:
                if now - _LAST_CLEANUP >= _CLEANUP_INTERVAL_SECONDS:
                    expired_before = now - period_seconds
                    stale_keys = []
                    for store_key, timestamps in _LIMIT_STORE.items():
                        active = [ts for ts in timestamps if ts > expired_before]
                        if active:
                            _LIMIT_STORE[store_key] = active
                        else:
                            stale_keys.append(store_key)
                    for stale_key in stale_keys:
                        _LIMIT_STORE.pop(stale_key, None)
                    _LAST_CLEANUP = now

                calls = [ts for ts in _LIMIT_STORE.get(index, []) if now - ts < period_seconds]
                if len(calls) >= max_calls:
                    abort(429)
                calls.append(now)
                _LIMIT_STORE[index] = calls

            return func(*args, **kwargs)

        return wrapped

    return decorator
