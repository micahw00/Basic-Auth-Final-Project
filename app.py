# Before running, make sure to run in the terminal:
# pip install bcrypt
# pip install flask

from flask import Flask, request, redirect, url_for, render_template, session
from database import get_db, init_db
import bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

init_db()


# ---------- PASSWORD VALIDATION ----------
def is_valid_password(password):
    return (
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Incorrect username or password"

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            error = "Fields cannot be empty"
        elif not is_valid_password(password):
            error = "Password must include uppercase, lowercase, number, and special character"
        else:
            conn = get_db()
            try:
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()

                return redirect(url_for("login"))
            except:
                conn.rollback()
                error = "Username already exists or error occurred"
            finally:
                conn.close()

    return render_template("register.html", error=error)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))
    
    #if request.method == "GET":
    if request.method == "POST":
        message = request.form["message"].strip()
        
        conn = get_db()
        conn.execute(
                    "INSERT INTO messages (message) VALUES (?)",
                    (message,)
                )
        conn.commit()
        conn.close()
    
    # TODO: Connect to the database
    conn = get_db()

    # TODO: Get all entries that belong to the logged-in user
    # Example:
    messages = conn.execute("SELECT * FROM messages").fetchall()

    # TODO: Close the connection
    conn.close()

    # TODO: Pass entries into your template
    # Example:
    return render_template("dashboard.html", messages=messages, username=session["user"])

    # TEMPORARY (remove later)
    # return render_template("dashboard.html", username=session["user"])


# ---------- CREATE ----------
# TODO: Create a route like /create
# This page should:
# - Show a form (GET)
# - Save data to the database (POST)
# - Redirect back to dashboard
# NOTE: Remove the triple """ before and after each route to 'uncomment'
"""
@app.route("/message_board", methods=["GET", "POST"])
def message_board():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        #author = request.form["author"].strip
        #message = request.form["message"].strip()
        conn = get_db()
        #message = request.form["message"]
        #author = request.form["author"]
    #messages = e_conn.execute("GET FROM messages (message, author) VALUES (?, ?)",
                    #(message, username)
                #).fetchall()
        messages = conn.execute("SELECT * FROM messages").fetchall()
        #author = conn.execute("SELECT * FROM messages", (author,)).fetchone()
        conn.close()
    #e_conn = get_messages_db
    
    #if request.method == "POST":
       # message = request.form["message"].strip()
        #author = request.form["username"].strip()

        # TODO: Connect to database

        # TODO: Insert into entries table
        # IMPORTANT: include session["user"]

        # TODO: Commit and close

        #return redirect(url_for("dashboard"))

    return render_template("message_board.html", username=session["user"])
#"""

# ---------- UPDATE ----------
# TODO: Create a route like /edit/<id>
# This page should:
# - Load existing data
# - Show it in a form
# - Update the database on submit

"""
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))

    # TODO: Connect to database

    # TODO: Get entry WHERE id AND user
    # This prevents editing other users' data

    # if not entry:
    #     return "Not allowed"

    if request.method == "POST":
        # TODO: Get updated form data

        # TODO: Update database
        # IMPORTANT: include id AND session["user"]

        # TODO: Commit and close

        return redirect(url_for("dashboard"))

    return render_template("edit.html", entry=entry)
"""

# ---------- DELETE ----------
# TODO: Create a route like /delete/<id>
# This should:
# - Delete an entry from the database
# - Redirect back to dashboard

"""
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))

    # TODO: Connect to database

    # TODO: Delete entry WHERE id AND user

    # TODO: Commit and close

    return redirect(url_for("dashboard"))
"""


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)