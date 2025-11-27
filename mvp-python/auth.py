from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_func):
    """
    Декоратор для захисту роутів:
    користувач має бути залогінений.
    """

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Спочатку увійдіть у систему", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view

