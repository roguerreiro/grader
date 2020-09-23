### Code for apology and login_required from CS50 Finance (pset8) file "helpers.py"

import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def add(cgs):
    """Return sum of class grades"""
    sum = 0
    for i in cgs:
        if i:
            sum += float(i)
    return sum

def count(cgs):
    """Return number of class grades"""
    count = 0
    for i in cgs:
        if i:
            count += 1
    return count

def cgavg(sum, count):
    """Calculate CG average"""
    if count == 0:
        return 0
    else:
        return (sum / count)

def approx(number):
    value = str(number)
    point = round(number - int(value[0]), 5)

    if 0 < point < 0.5:
        if point >= 0.26:
            return(int(value[0]) + 0.5)
        else:
            return(int(value[0]))
    elif 0.5 < point < 1:
        if point < 0.76:
            return(int(value[0]) + 0.5)
        else:
            return(int(value[0]) + 1)
    else:
        return(number)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
