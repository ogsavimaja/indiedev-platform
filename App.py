from flask import Flask, render_template, request, redirect, session
import sqlite3
import db
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_hex
import config
import announcements
import users

app = Flask(__name__)
app.secret_key = config.secret_key


# Render front page
@app.route("/")
def index():
    all_announcements = announcements.get_announcements()
    return render_template("index.html", announcements=all_announcements)


# Render error page
def errorpage(error_message, error_type):
    return render_template("errorpage.html", error_message=error_message, error_type=error_type)


# Render search page
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        query = request.args.get("query")
        print(query)
        results = announcements.search_announcements(query) if query else None
        return render_template("search.html", query=query, results=results)
    return redirect("/")


# Render announcement page
@app.route("/announcement/<int:announcement_id>")
def announcement(announcement_id):
    announcement = announcements.get_announcement(announcement_id)
    if not announcement:
        return errorpage("Announcement not found", "Error while loading announcement")
    
    result = announcements.get_one_announcement_classes(announcement_id)
    classes = result [0]
    lengths = result[1]
    return render_template("announcement.html", announcement=announcement, classes=classes, lengths=lengths)

# Render announcement creation page
@app.route("/new_announcement", methods=["GET", "POST"])
def new_announcement():
    if not session.get("username"):
        return redirect("/login")

    result = announcements.get_announcement_classes()
    all_classes = result[0]
    class_types = result[1]

    if request.method == "POST":
        title = request.form["name_of_the_game"]
        description = request.form["description"]
        download_link = request.form["download_link"]
        intented_price = request.form["intented_price"]
        age_restriction = request.form["age_restriction"]

        # Add classes into a list
        state = None
        classes = []
        for name in class_types.keys():
            result = request.form.getlist(name)
            if result != [""]:
                for value in result:
                    if value in all_classes[name]:
                        classes.append((name, value))
                        if name == "State":
                            state = True
                    else:
                        return errorpage("Invalid input", "Error while creating announcement")

        # Validate user input
        if not title or not description or not state:
            return errorpage("All fields marked with * are required", "Error while creating announcement")
        if len(title) > 70:
            return errorpage("Title must be less than 70 characters", "Error while creating announcement")
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

        # Insert data into database
        announcements.add_announcement(session["user_id"], title, download_link, description, intented_price, age_restriction, classes)

        return redirect("/")
    return render_template("new_announcement.html", classes=all_classes, class_types=class_types)


# Render announcement edit page
@app.route("/announcement/<int:announcement_id>/edit", methods=["GET", "POST"])
def edit_announcement(announcement_id):
    # Check if announcement excist, user is logged in and authorized to remove announcement
    announcement = announcements.get_announcement(announcement_id)
    if not announcement:
        return errorpage("Announcement not found", "Error while editing announcement")
    if not session.get("username"):
        return redirect("/login")
    if session["user_id"] != announcement["user_id"]:
        return errorpage("You are not authorized to edit this announcement", "Error while editing announcement")

    result = announcements.get_announcement_classes()
    all_classes = result[0]
    class_types = result[1]
    right_classes = announcements.get_one_announcement_classes(announcement_id)[0]

    # Check if user is sending the edit form or just requesting the page
    if request.method == "POST":
        if "confirm" in request.form:
            title = request.form["name_of_the_game"]
            description = request.form["description"]
            download_link = request.form["download_link"]
            intented_price = request.form["intented_price"]
            age_restriction = request.form["age_restriction"]

            # Add classes into a list
            state = None
            classes = []
            for name in class_types.keys():
                result = request.form.getlist(name)
                if result != [""]:
                    for value in result:
                        if value in all_classes[name]:
                            classes.append((name, value))
                            if name == "State":
                                state = True
                        else:
                            return errorpage("Invalid input", "Error while creating announcement")

            # Validate user input
            if not title or not description or not state:
                return errorpage("All fields marked with * are required", "Error while editing announcement")
            if len(title) > 70:
                return errorpage("Title must be less than 70 characters", "Error while editing announcement")
            if len(description) > 1000:
                return errorpage("Description must be less than 1000 characters", "Error while editing announcement")
            if download_link:
                if not download_link.startswith("http"):
                    return errorpage("Invalid download link", "Error while editing announcement")
            if intented_price:
                if not intented_price.isdigit():
                    return errorpage("Price must be a number (0 for free), (currently supports only integers)", "Error while editing announcement")
            if age_restriction:
                if not age_restriction.isdigit():
                    return errorpage("Age restriction must be a number", "Error while editing announcement")

            # Update announcement in database
            announcements.update_announcement(announcement_id, title, download_link, description, intented_price, age_restriction, classes)
            return redirect("/announcement/" + str(announcement_id))
        return redirect("/announcement/" + str(announcement_id))
    return render_template("edit_announcement.html", announcement=announcement, classes=all_classes, class_types=class_types, right_classes=right_classes)


# Render announcement remove page
@app.route("/announcement/<int:announcement_id>/remove", methods=["GET", "POST"])
def remove_announcement(announcement_id):
    # Check if announcement excist, user is logged in and authorized to remove announcement
    announcement = announcements.get_announcement(announcement_id)
    if not announcement:
        return errorpage("Announcement not found", "Error while removing announcement")
    if not session.get("username"):
        return redirect("/login")
    if session["user_id"] != announcement["user_id"]:
        return errorpage("You are not authorized to remove this announcement", "Error while removing announcement")

    if request.method == "POST":
        if "remove" in request.form:
            announcements.remove_announcement(announcement_id)
            return redirect("/")
        return redirect("/announcement/" + str(announcement_id))
    return render_template("remove_announcement.html", announcement=announcement)

# Render user page
@app.route("/user/<int:user_id>")
def user(user_id):
    user_data = db.query("SELECT username FROM Users WHERE id = ?", [user_id])
    if not user_data:
        return errorpage("User not found", "Error while loading user")
    user_data = user_data[0]
    user_announcements = users.get_user_announcements(user_id)
    return render_template("userpage.html", user=user_data, announcements=user_announcements)


# Render login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is sending the login form or just requesting the page
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
@app.route("/register", methods=["GET", "POST"])
def register():
    # Check if user is sending the register form or just requesting the page
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        salt = token_hex(10)
        confirm_password = request.form["confirm_password"]
        email = request.form["email"]

        # Validate user input
        if not username or not password or not confirm_password:
            return errorpage("All fields except email are required", "Error while creating account")
        if len(password) < 8:
            return errorpage("Password must be at least 8 characters long", "Error while creating account")
        if len(username) < 3:
            return errorpage("Username must be at least 3 characters long", "Error while creating account")
        if password != confirm_password:
            return errorpage("Passwords do not match", "Error while creating account")
        if email:
            if not "@" in email or not "." in email:
                return errorpage("Invalid email", "Error while creating account")

        # Check if username already exists, if not, create account
        try:
            sql_query = """INSERT INTO Users (username, salt, hashed_password, email)
                        VALUES (?, ?, ?, ?)"""
            db.execute(sql_query, [username, salt, generate_password_hash(password+salt), email])
        except sqlite3.IntegrityError:
            return errorpage("Username already exists", "Error while creating account")
        return render_template("account_created.html")
    return render_template("register.html")



# Allows the app to run in IDE terminal in debug mode
if __name__ == "__main__":
    app.run(debug=True)
