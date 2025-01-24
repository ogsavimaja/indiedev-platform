from flask import Flask, render_template, request, redirect
import sqlite3
import db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

language="english"

# Pass the required route to the decorator
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form["username"]
    password = request.form["password"]
    if not username or not password:
        return "ERROR: All fields are required"
    
    user_data = db.query("SELECT * FROM Users WHERE username = ?", [username])
    if not user_data:
        return "ERROR: Invalid username"
    
    user_data = user_data[0]
    if not check_password_hash(user_data["hashed_password"], password):
        return "ERROR: Invalid password"
    
    return "Logged in"

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    email = request.form["email"]
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
        
    try:
        db.execute("INSERT INTO Users (username, hashed_password, email) VALUES (?, ?, ?)", [username, generate_password_hash(password), email])
    except sqlite3.IntegrityError:
        return "ERROR: Username already exists"
    
    return "Account created"



if __name__ == "__main__":
    app.run(debug=True)