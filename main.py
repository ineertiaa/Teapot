import mysql.connector
from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import re
import secrets

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

username = ""
password = ""
special_chars = re.compile(r"[!@%#]")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

@app.route("/api/process", methods=["post"])
def process():
    data = request.get_json()
    cursor = database.cursor(buffered=True)

    if (data and data.get("type") == "delete"):
        try:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (data.get("task_id"),))
            database.commit()
            cursor.close()

            return jsonify({"success": True, "message": "task deleted."}), 200
        except Exception as e:
            database.rollback()
            cursor.close()
            return jsonify({"success": False, "message": f"couldn't delete task. str({e})"}), 500

    if (data and data.get("type") == "login"):
        try:
            cursor.execute("SELECT 1 FROM users WHERE username = %s AND password = %s", (username, password)) # to protect against injections.
            database.commit()
            cursor.close()

            return jsonify({"success": True, "message": "logged in!"}), 200
        except Exception as e:
            database.rollback()
            cursor.close()
            return jsonify({"success": False, "message": f"couldn't login :( str({e})"}), 500

    if (data and data.get("type") == "markdone"):
        try:
            cursor.execute("SELECT 1 FROM tasks WHERE id = %s", (data.get("task_id"),))
            if (cursor.fetchone()):
                status_value = 1 if data.get("done") else 0
                cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status_value, data.get("task_id")))
                database.commit()
                cursor.close()
                return jsonify({"success": True, "message": "set status!"}), 200
        except Exception as e:
            database.rollback()
            cursor.close()
            return jsonify({"success": False, "message": f"couldn't set status :( str({e})"}), 500

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

            session["username"] = username

            cursor = database.cursor(buffered=True)
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
                    cursor.close()
                    return redirect(url_for("home"))
            
            cursor.close()

        elif ("login_user" in request.form):
            username = request.form.get("login_user")
            password = request.form.get("login_pass")

            cursor = database.cursor(buffered=True)
            cursor.execute("SELECT 1 FROM users WHERE username = %s AND password = %s", (username, password))

            if (not cursor.fetchone()):
                error = "Username or password incorrect. Please try again."
            else:
                session["username"] = username
                cursor.close()
                return redirect(url_for("home"))
            
            cursor.close()

    return render_template("index.html", error=error)

def get_tasks(user):
    try:
        cursor = database.cursor(buffered=True)
        cursor.execute("SELECT * FROM tasks WHERE assigned_to = %s OR created_by = %s", (user, user))

        tasks = cursor.fetchall()
        cursor.close()

        return tasks
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return []



@app.route("/home", methods=["post", "get"])
def home():
    fetched_tasks = get_tasks(session.get("username"))

    if (request.method == "POST"):
        if ("title" in request.form):
            new_title = request.form.get("title")
            new_desc = request.form.get("description")
            assigned = request.form.get("assigned_to")
            priority = request.form.get("priority")
            due = request.form.get("due_date")

            cursor = database.cursor(buffered=True)
            cursor.execute("INSERT INTO tasks(title, description, assigned_to, created_by, status, priority, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", (new_title, new_desc, assigned, session.get("username"), False, priority, due))
            database.commit()
            cursor.close()
            
            # Re-fetch tasks after creating new one
            fetched_tasks = get_tasks(session.get("username"))

    return render_template("home.html", tasks=fetched_tasks)

if (__name__ == "__main__"):
    app.run()

# ** I decided to execute the commands inside of the python file itself for ease of access.

# TODO: Make it so team manager see all tasks
# TODO: Add task adding to the html page

cursor = database.cursor(buffered=True)

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
    status BOOL NOT NULL,
    priority VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL
    )"""
)

database.commit()
cursor.close()