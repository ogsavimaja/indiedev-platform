from flask import Flask, render_template, request, redirect, session
import sqlite3
import db
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_hex
import config

app = Flask(__name__)
app.secret_key = config.secret_key

# TODO - Add a language selector
# language="english"

# Render front page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_announcement", methods=["GET", "POST"])
def new_announcement():
    if not session.get("username"):
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        intented_price = request.form["intented_price"]
        age_restriction = request.form["age_restriction"]

        # Validate user input
        if not title or not description:
            return "ERROR: All fields marked with * are required"
        if intented_price:
            if not intented_price.isdigit():
                return "ERROR: Price must be a number"
        if age_restriction:
            if not age_restriction.isdigit():
                return "ERROR: Age restriction must be a number"

        # Insert announcement into database
        sql_query = """INSERT INTO Announcements (user_id, title, about, intented_price, intented_age_restriction)
                       VALUES (?, ?, ?, ?, ?)"""
        db.execute(sql_query, [session["user_id"], title, description, intented_price, age_restriction,])
        return redirect("/")

    return render_template("new_announcement.html")

# Render login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return "ERROR: All fields are required"

        # Check if user exists
        sql_query = """SELECT *
                       FROM Users
                       WHERE username = ?"""
        user_data = db.query(sql_query, [username])
        if not user_data:
            return "ERROR: Invalid Credentials"

        # Check if password is correct
        user_data = user_data[0]
        if check_password_hash(user_data["hashed_password"], (password + user_data["salt"])):
            session["username"] = user_data["username"]
            session["user_id"] = user_data["id"]
            return redirect("/")

        return "ERROR: Invalid Credentials"

    return render_template("login.html")

# Log out user
@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")

# Render register page
@app.route("/register")
def register():
    return render_template("register.html")

# Create user's account
@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password = request.form["password"]
    salt = token_hex(10)
    confirm_password = request.form["confirm_password"]
    email = request.form["email"]

    # Validate user input
    if not username or not password or not confirm_password:
        return "ERROR: All fields except email are required"
    if len(password) < 8:
        return "ERROR: Password must be at least 8 characters long"
    if len(username) < 3:
        return "ERROR: Username must be at least 3 characters long"
    if password != confirm_password:
        return "ERROR: Passwords do not match"
    if email:
        if not ("@" and "." in email):
            return "Invalid email"


    # Check if username already exists
    try:
        sql_query = """INSERT INTO Users (username, salt, hashed_password, email)
                       VALUES (?, ?, ?, ?)"""
        db.execute(sql_query, [username, salt, generate_password_hash(password + salt), email])
    except sqlite3.IntegrityError:
        return "ERROR: Username already exists"

    return "Account created"




# Allows the app to run in IDE terminal in debug mode
if __name__ == "__main__":
    app.run(debug=True)