from functools import wraps
from flask import current_app
from flask_login import login_required

def conditional_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get("ENV", "production") == "development":
            return f(*args, **kwargs)
        else:
            return login_required(f)(*args, **kwargs)
    return decorated_function
