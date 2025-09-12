import re
import requests

from flask import redirect, render_template, session, request, url_for
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



# Decorator
def check_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("checked"):
            # store where user was going, so we can return later
            session["next_url"] = request.path
            return redirect(url_for("check"))
        return f(*args, **kwargs)
    return decorated_function

def norm(input):
    if input:
        return re.sub(r'\D', '', input)
    else:
        return input