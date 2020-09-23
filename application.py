import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, add, count, cgavg, approx

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///grader.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show user's grades for selected trimester"""
    if request.method == "POST":
        trimester = request.form.get("trimester")
        user = session["user_id"]
        index = db.execute("SELECT * FROM grades WHERE id=:user AND trimester=:trimester ORDER BY subject ASC", user=user, trimester=trimester)
        for subject in index:
            test = subject["test"]
            cg1 = subject["cg1"]
            cg2 = subject["cg2"]
            cg3 = subject["cg3"]
            cg4 = subject["cg4"]
            cg5 = subject["cg5"]
            cgs = [cg1, cg2, cg3, cg4, cg5]
            if subject["subject"] in ["RE", "Sociology", "Philosophy"]:
                if test:
                    average = (test + cgavg(add(cgs), count(cgs))) / 2
                else:
                    average = cgavg(add(cgs), count(cgs)) / 2
            else:
                if test:
                    average = test * 0.4 + cgavg(add(cgs), count(cgs)) * 0.6
                else:
                    average = cgavg(add(cgs), count(cgs)) * 0.6
            rounded = approx(average)
            subject.update({"average": round(average, 5)})
            subject.update({"approx": rounded})
        return render_template("grades.html", trimester=trimester, index=index)
    else:
        return render_template("index.html")


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    """Insert inputted values into SQL database"""
    if request.method == "POST":
        user = session["user_id"]
        trimester = request.form.get("trimester")
        subject = request.form.get("subject")
        evaluation = request.form.get("evaluation")
        grade = float(request.form.get("grade"))
        description = request.form.get("description")

        if not trimester or not subject or not evaluation:
            return apology("Please fill in every field!")
        else:
            if grade < 0 or grade > 10:
                return apology("Please insert a grade between 0 and 10!")
            else:
                desc = {
                    "test": "desct",
                    "cg1": "desc1",
                    "cg2": "desc2",
                    "cg3": "desc3",
                    "cg4": "desc4",
                    "cg5": "desc5"
                }
                desc = desc[evaluation]
                if db.execute("SELECT * FROM grades WHERE id=:user AND trimester=:trimester AND subject=:subject", user=user, trimester=trimester, subject=subject):
                    db.execute("UPDATE grades SET :evaluation=:grade, :desc=:description WHERE id=:user AND trimester=:trimester AND subject=:subject", evaluation=evaluation, grade=grade, desc=desc, description=description, user=user, trimester=trimester, subject=subject)
                else:
                    db.execute("INSERT INTO grades (id, trimester, subject, :evaluation, :desc) VALUES (:user, :trimester, :subject, :grade, :description)", evaluation=evaluation, desc=desc, user=user, trimester=trimester, subject=subject ,grade=grade, description=description)
                evaluation = evaluation.capitalize()
                return render_template("inserted.html", trimester=trimester, subject=subject, evaluation=evaluation, grade=grade, description=description)
    else:
        return render_template("insert.html")


@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    """Calculate necessary score on an activity based on inputted values"""
    if request.method == "POST":
        subject = request.form.get("subject")
        test = request.form.get("test")
        cg1 = request.form.get("cg1")
        cg2 = request.form.get("cg2")
        cg3 = request.form.get("cg3")
        cg4 = request.form.get("cg4")
        cg5 = request.form.get("cg5")
        cgs = [cg1, cg2, cg3, cg4, cg5]
        average = float(request.form.get("average"))
        if subject == "1":
            if test:
                test = float(test)
                grade = ((count(cgs) + 1) * (average - 0.24 - (test * 0.4))) / 0.6 - add(cgs)
                evaluation = "test"
            else:
                grade = (average - 0.24 - cgavg(add(cgs), count(cgs)) * 0.6) / 0.4
                evaluation = "class grade"
        else:
            if test:
                test = float(test)
                grade = (count(cgs) + 1) * (2 * (average - 0.24) - test) - add(cgs)
                evaluation = "test"
            else:
                grade = 2 * (average - 0.24) - cgavg(add(cgs), count(cgs))
                evaluation = "class grade"
        return render_template("calculated.html", grade=round(grade, 3), evaluation=evaluation)
    else:
        return render_template("calculator.html")


# Code from CS50 Finance distribution code
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Code from CS50 Finance distribution code
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if username in db.execute("SELECT username FROM users"):
            return apology("This username is already taken!", 403)
        elif username == "":
            return apology("Please insert a username!", 403)
        elif password == "":
            return apology("Please insert a password!", 403)
        elif password != confirm:
            return apology("Passwords do not match!", 403)
        elif len(password) < 8:
            return apology("Password must have at least 8 characters!", 403)
        else:
            hashpass = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashpass)", username=username, hashpass=hashpass)
            return redirect("/")


# Code from CS50 Finance distribution code
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Code from CS50 Finance distribution code
# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
