from flask import Flask, render_template, request, redirect, session
import sqlite3
import db
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_hex
import config
import announcements

app = Flask(__name__)
app.secret_key = config.secret_key


# Render front page
@app.route("/")
def index():
    all_announcements = announcements.get_announcements()
    return render_template("index.html", announcements=all_announcements)

# Render announcement page
@app.route("/announcement/<int:announcement_id>")
def announcement(announcement_id):
    announcement = announcements.get_announcement(announcement_id)
    return render_template("announcement.html", announcement=announcement)

#render error page
def errorpage(error_message, error_type):
    return render_template("errorpage.html", error_message=error_message, error_type=error_type)

# Render announcement creation page
@app.route("/new_announcement", methods=["GET", "POST"])
def new_announcement():
    if not session.get("username"):
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        download_link = request.form["download_link"]
        intented_price = request.form["intented_price"]
        age_restriction = request.form["age_restriction"]

        # Validate user input
        if not title or not description:
            return errorpage("All fields marked with * are required", "Error while creating announcement")
        if len(title) > 100:
            return errorpage("Title must be less than 100 characters", "Error while creating announcement")
        if len(description) > 1000:
            return errorpage("Description must be less than 1000 characters", "Error while creating announcement")
        if download_link:
            if not download_link.startswith("http"):
                return errorpage("Invalid download link", "Error while creating announcement")
        if intented_price:
            if not intented_price.isdigit():
                return errorpage("Price must be a number (0 for free), (currently supports only integers)", "Error while creating announcement")
        if age_restriction:
            if not age_restriction.isdigit():
                return errorpage("Age restriction must be a number", "Error while creating announcement")


        # Insert announcement into database
        announcements.add_announcement(session["user_id"], title, download_link, description, intented_price, age_restriction)
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
            return errorpage("All fields are required", "Error while logging in")

        # Check if user exists
        sql_query = """SELECT id, username, hashed_password, salt
                       FROM Users
                       WHERE username = ?"""
        user_data = db.query(sql_query, [username])
        if not user_data:
            return errorpage("Invalid Credentials", "Error while logging in")

        # Check if password is correct
        user_data = user_data[0]
        if check_password_hash(user_data["hashed_password"], (password + user_data["salt"])):
            session["username"] = user_data["username"]
            session["user_id"] = user_data["id"]
            return redirect("/")
        return errorpage("Invalid Credentials", "Error while logging in")

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
        return errorpage("All fields marked with * are required", "Error while creating account")
    if len(password) < 8:
        return errorpage("Password must be at least 8 characters long", "Error while creating account")
    if len(username) < 3:
        return errorpage("Username must be at least 3 characters long", "Error while creating account")
    if password != confirm_password:
        return errorpage("Passwords do not match", "Error while creating account")
    if email:
        if not ("@" and "." in email):
            return errorpage("Invalid email", "Error while creating account")


    # Check if username already exists, if not, create account
    try:
        sql_query = """INSERT INTO Users (username, salt, hashed_password, email)
                       VALUES (?, ?, ?, ?)"""
        db.execute(sql_query, [username, salt, generate_password_hash(password+salt), email])
    except sqlite3.IntegrityError:
        return errorpage("Username already exists", "Error while creating account")

    return render_template("account_created.html")




# Allows the app to run in IDE terminal in debug mode
if __name__ == "__main__":
    app.run(debug=True)