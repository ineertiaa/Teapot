import mysql.connector
from flask import Flask, redirect, url_for, render_template, request
import re

import os
from dotenv import load_dotenv

load_dotenv()
sql_pass = os.getenv("SQL_PASSWORD")

username = ""
password = ""
special_chars = re.compile(r"!@%#")

app = Flask(__name__)

@app.route("/", methods=["post", "get"])
def startpage():
    # ! Note to self: DO NOT USE GLOBAL WITH WEB!

    error = ""

    if (request.method == "POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))

        if (cursor.fetchone()):
            error = f"Username: {username} already exists! Please make a unique name."
        elif (len(password) < 8):
            error = "Password must have at least 8 characters"
        elif (special_chars.search(password) is None):
            #TODO: fix this error showing up even though there is a special character.
            error = "Password must contain atleast one special character"
        else:
            error = ""
            cursor.execute("INSERT INTO users(username, password) VALUES (%s, %s)", (username, password))

    return render_template("index.html", error=error)

@app.route("/home")
def home():
    return "<h1>Home</h1>"

if (__name__ == "__main__"):
    app.run()

database = mysql.connector.connect(
    host="localhost",
    user="",
    password=sql_pass,
    database="teapot"
)

cursor = database.cursor(buffered=True)

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

user_input = ""
pass_input = ""

def login():
    global user_input
    global pass_input

    user_input = input("Enter your username: ")
    pass_input = input("Enter your password: ")

    cursor.execute("SELECT 1 FROM users WHERE username = %s", (user_input,)) # %s is a placeholder for a variable.

    if (cursor.fetchone()):
        print("Found user and logged in!")
    else:
        print("didn't find user, Please try again. \n")
        login()

def create_acc(username, password):

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    print("Created account successfully.")

def create_task():
    title = input("enter title: ")
    description = input("enter desc: ")
    assigned_to = input("assign to: ")
    status = input("status: ")
    priority = input("priority: ")
    due_date = input("due date: YYYY-MM-DD ")

    cursor.execute("SELECT * FROM users WHERE username = %s", (assigned_to,))

    if (not cursor.fetchone()):
        print("didn't find user, Please try again.")

    task_dat = (title, description, assigned_to, user_input, status, priority, due_date)

    insert = """INSERT INTO tasks (title, description, assigned_to, created_by, status, priority, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    cursor.execute(insert, task_dat)

def change_status():
    task_title = input("Input the task title you would like to change the status of: ")

    cursor.execute("SELECT 1 FROM tasks WHERE title = %s", (task_title,))

    if (cursor.fetchone()):
        print("Task found!")
        changed_status = input("Enter what you would like the status to be changed to: ")
        cursor.execute("UPDATE tasks SET status = %s WHERE title = %s", (changed_status, task_title))

def delete_task():
    task_title = input("Input the task title you would like to delete: ")

    cursor.execute("SELECT 1 FROM tasks WHERE title = %s", (task_title,))

    if (cursor.fetchone()):
        cursor.execute("DELETE FROM tasks WHERE title = %s", (task_title,))
        print(f"Successfully deleted {task_title}!")
    else:
        print("Couldn't find task name.")

login_confirm = int(input("1. Login" \
" 2. Create account "))

if (login_confirm == 1):
    login()
else:
    create_acc()

task_confirm = int(input("1. Create task \n 2. Delete task \n 3. Change task status"))

if (task_confirm == 1):
    create_task()
elif (task_confirm == 2):
    delete_task()
elif (task_confirm == 3):
    change_status()
else:
    print("Please enter 1, 2 or 3.")

cursor.execute("SELECT * FROM users")
cursor.execute("SELECT * FROM tasks")

fetched_stuff = cursor.fetchall()

database.commit()

cursor.execute("SELECT * FROM tasks WHERE assigned_to = %s", (user_input,))
cursor.execute("SELECT * FROM tasks WHERE created_by = %s", (user_input,))

for row in cursor.fetchall():
    print(row)

print(f"rows: {cursor.rowcount}")