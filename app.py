import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta, datetime  
import calendar

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///timesheet.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")

@app.route('/timesheet')
@app.route('/timesheet/all')
@login_required
def all_tasks():
    user_id = session.get("user_id")
    timesheets = db.execute("select p.p_name,  t.bu_vertical, t.name as Task, t.type, t.date, t.duration_minutes as Duration, t.description from projects p inner join tasks t on project_id = p.id where t.user_id = ?;",  user_id)
    return render_template('timesheet.html', timesheets=timesheets)

@app.route('/timesheet/today')
@login_required
def today_tasks():
    user_id = session.get("user_id")
    today = date.today().strftime("%Y-%m-%d")
    timesheets = db.execute("select p.p_name,  t.bu_vertical, t.name as Task, t.type, t.date, t.duration_minutes as Duration, t.description from projects p inner join tasks t on project_id = p.id where t.user_id = ? and t.date = ?",  user_id, today)
    return render_template('timesheet.html', timesheets=timesheets)

@app.route('/timesheet/weekly')
@login_required
def weekly_tasks():
    user_id = session.get("user_id")
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Format the dates as "year-month-day"
    monday = start_of_week.strftime("%Y-%m-%d")
    sunday = end_of_week.strftime("%Y-%m-%d")

    timesheets = db.execute("select p.p_name,  t.bu_vertical, t.name as Task, t.type, t.date, t.duration_minutes as Duration, t.description from projects p inner join tasks t on project_id = p.id where t.user_id = ? and t.date between ? and ?",  user_id, monday, sunday)
    return render_template('timesheet.html', timesheets=timesheets)


@app.route('/timesheet/monthly')
@login_required
def monthly_tasks():
    user_id = session.get("user_id")
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    _, last_day_of_month = calendar.monthrange(today.year, today.month)
    end_of_month = date(today.year, today.month, last_day_of_month)

    timesheets = db.execute("select p.p_name,  t.bu_vertical, t.name as Task, t.type, t.date, t.duration_minutes as Duration, t.description from projects p inner join tasks t on project_id = p.id where t.user_id = ? and t.date between ? and ?",  user_id, start_of_month, end_of_month)
    return render_template('timesheet.html', timesheets=timesheets)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/projects")
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    user_id = session.get("user_id")

    if request.method == "GET":
        projectRecords = db.execute("select * from Projects where user_id = ? and status = ?", user_id, 'Active')


    return render_template("index.html", projectRecords=projectRecords)
    """Get stock quote."""
    return apology("TODO")


@app.route("/projectclose", methods=["GET", "POST"])
@login_required
def projectClose():

    userID = session.get("user_id")
    if request.method == "POST":
        projectID = request.form.get("closeproject")
        db.execute("update projects set status = ? where id = ? and user_id = ?", 'Closed', projectID, userID)
    return redirect("/")


@app.route("/addproject", methods=["GET", "POST"])
@login_required
def addProject():
    user_id = session.get("user_id")
    if request.method == "POST":
        projectName = request.form.get("p_name")
        if not projectName:
            flash("Missing Project Name")
            return redirect("/")
        db.execute("INSERT INTO Projects (p_name, user_id, status) VALUES (?, ?, ?)", projectName, user_id, 'Active')

    return redirect("/")

@app.route("/addtask", methods=["GET", "POST"])
@login_required
def addTask():
    user_id = session.get("user_id")
    if request.method == "POST":
        projectID = request.form.get("p_id")
        buVertical = request.form.get("buvertical")
        taskName = request.form.get("task")
        taskType = request.form.get("type")
        date = request.form.get("date")
        durationHours = request.form.get("hours")
        durationMinutes = request.form.get("minutes")
        description = request.form.get("description")

        if not taskName or not durationHours or not durationMinutes or not description:
            flash("All the fields are required")
            return redirect("/")

        durationHours = int(durationHours)
        durationMinutes = int(durationMinutes)
        durationMinutes = (durationHours*60)+durationMinutes
        
        db.execute("INSERT INTO tasks (bu_vertical, name, type, date, duration_minutes, description, project_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", buVertical, taskName, taskType, date, durationMinutes, description, projectID, user_id)
    
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Validate submission
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
    # Validate inputs
        if not username or not password or not confirmation:
            return apology("All fields are required.")

        if password != confirmation:
            return apology("Passwords do not match.")

        user_exists = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user_exists) == 1:
            return apology("username already exist", 400)

        hash = generate_password_hash(password, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        flash ("Registered!")
    return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Show settings"""
    # Query database
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    return render_template("settings.html", username=username[0]['username'])


@app.route("/passwordupdate", methods=["GET", "POST"])
@login_required
def passwordupdate():
    """Show settings"""

    if request.method == "POST":

        # Validate submission
        currentpassword = request.form.get("currentpassword")
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure password == confirmation
        if not (newpassword == confirmation):
            return apology("the passwords do not match", 400)

        # Ensure password not blank
        if currentpassword == "" or newpassword == "" or confirmation == "":
            return apology("input is blank", 400)

       # Ensure password is correct
        if not check_password_hash(rows[0]["hash"], currentpassword):
            return apology("invalid password", 403)
        else:
            hashcode = generate_password_hash(newpassword, method='pbkdf2', salt_length=16)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashcode, session["user_id"])

        # Redirect user to settings
        return redirect("/settings")

    else:
        return render_template("passwordupdate.html")
