from functools import wraps

from flask import abort
from flask_login import current_user


def roles_required(*roles: str):
    allowed = {role.lower() for role in roles}

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.role or current_user.role.name.lower() not in allowed:
                abort(403)
            return func(*args, **kwargs)

        return wrapped

    return decorator
