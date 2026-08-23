import mysql.connector
from flask import Flask, redirect, url_for, render_template, request
import re

import os
from dotenv import load_dotenv

load_dotenv()
sql_pass = os.getenv("SQL_PASSWORD")

database = mysql.connector.connect(
    host="localhost",
    user="",
    password=sql_pass,
    database="teapot"
)

cursor = database.cursor(buffered=True)

username = ""
password = ""
special_chars = re.compile(r"[!@%#]")

app = Flask(__name__)

@app.route("/", methods=["post", "get"])
def startpage():
    # ! Note to self: DO NOT USE GLOBAL WITH WEB!

    error = None

    if (error == None):
        error = ""

    if (request.method == "POST"):
        if ("signup_user" in request.form):
            username = request.form.get("signup_user")
            password = request.form.get("signup_pass")

            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))

            if (cursor.fetchone()):
                error = f"Username: {username} already exists! Please make a unique name."
            else:
                if (not username or not password):
                    error = "Username and password must be filled!"
                elif (len(password) < 8):
                    error = "Password must have at least 8 characters"
                elif (special_chars.search(password) is None):
                    error = "Password must contain atleast one special character (!@%#)"
                else:
                    error = ""
                    cursor.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (username, password))
                    database.commit()
                    return redirect(url_for("home"))

        elif ("login_user" in request.form):
            username = request.form.get("login_user")
            password = request.form.get("login_pass")

            cursor.execute("SELECT 1 FROM users WHERE username = %s AND password = %s", (username, password))

            if (not cursor.fetchone()):
                error = "Username or password incorrect. Please try again."
            else:
                return redirect(url_for("home"))

    return render_template("index.html", error=error)

@app.route("/home")
def home():
    return "<h1>Home</h1>"

if (__name__ == "__main__"):
    app.run()

# ** I decided to execute the commands inside of the python file itself for ease of access.

# TODO: protect against sql injection attacks
# TODO: Make it so team manager see all tasks

cursor.execute(
    """CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
    )"""
)

cursor.execute(
    """CREATE TABLE IF NOT EXISTS tasks(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL
    )"""
)
# auto_increment primary key makes sql make a new value automatically, like how an ID would work.
# not null forces sql to give a value and cant be null.

fetched_stuff = cursor.fetchall()

database.commit()

for row in cursor.fetchall():
    print(row)

print(f"rows: {cursor.rowcount}")