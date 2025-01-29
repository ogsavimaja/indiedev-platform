from flask import Flask, render_template, request, redirect
import sqlite3
import db
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_hex

app = Flask(__name__)

language="english"

# Render front page
@app.route("/")
def index():
    return render_template("index.html")

# Render login page
@app.route("/login")
def login():
    return render_template("login.html")

# Authenticate user
@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form["username"]
    password = request.form["password"]
    if not username or not password:
        return "ERROR: All fields are required"
    
    # Check if user exists
    user_data = db.query("SELECT * FROM Users WHERE username = ?", [username])
    if not user_data:
        return "ERROR: Invalid Credentials"
    
    # Check if password is correct
    user_data = user_data[0]
    if not check_password_hash(user_data["hashed_password"], (password + user_data["salt"])):
        return "ERROR: Invalid Credentials"
    
    return "Logged in"

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
        db.execute("INSERT INTO Users (username, salt, hashed_password, email) VALUES (?, ?, ?, ?)", [username, salt, generate_password_hash(password + salt), email])
    except sqlite3.IntegrityError:
        return "ERROR: Username already exists"
    
    return "Account created"


# Allows the app to run on IDE in debug mode
if __name__ == "__main__":
    app.run(debug=True)