import time
from functools import wraps
from threading import Lock

from flask import abort, request


_LIMIT_STORE: dict[tuple[str, str], list[float]] = {}
_LIMIT_LOCK = Lock()


def rate_limit(key: str, max_calls: int, period_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            remote = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            now = time.time()
            index = (key, remote)

            with _LIMIT_LOCK:
                calls = [ts for ts in _LIMIT_STORE.get(index, []) if now - ts < period_seconds]
                if len(calls) >= max_calls:
                    abort(429)
                calls.append(now)
                _LIMIT_STORE[index] = calls

            return func(*args, **kwargs)

        return wrapped

    return decorator
