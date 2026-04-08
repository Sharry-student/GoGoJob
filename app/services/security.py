import re
from functools import wraps

from flask import abort
from flask_login import current_user


def validate_password_policy(password: str):
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not re.search(r"[A-Z]", password):
        return False, "密码需包含至少1个大写字母"
    if not re.search(r"[a-z]", password):
        return False, "密码需包含至少1个小写字母"
    if not re.search(r"\d", password):
        return False, "密码需包含至少1个数字"
    if not re.search(r"[^\w\s]", password):
        return False, "密码需包含至少1个特殊字符"
    return True, "ok"


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
