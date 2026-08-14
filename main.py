import mysql.connector
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

# ** I decided to execute the commands inside of the python file itself for ease of access.

# TODO: protect against sql injection attacks

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

login_confirm = int(input("1. Login \n 2. Create account"))

if (login_confirm == 1):
    login_user = input("enter your user.")
    login_pass = input("enter your password.")

    cursor.execute("SELECT 1 FROM users WHERE username = %s", (login_user,)) # %s is a placeholder for a variable.

    if (cursor.fetchone()):
        print("found account, logging in")
    else:
        print("account not found, create one.")
elif (login_confirm == 2):
    new_user = input("enter a unique username.")
    new_pass = input("enter a strong password.")

    createacc_dat = (new_user, new_pass)
    createacc_insert = """INSERT INTO users (username, password) VALUES (%s, %s)"""

    cursor.execute(createacc_insert, createacc_dat)
else:
    print("Skipping...")
    pass

test = input("make new task? (Y/n) ")

if (test == "Y" or test == "y"):
    title = input("enter title: ")
    description = input("enter desc: ")
    assigned_to = input("assign to: ")
    created_by = input("who by: ")
    status = input("status: ")
    priority = input("priority: ")
    due_date = input("due date: YYYY-MM-DD ")

    task_dat = (title, description, assigned_to, created_by, status, priority, due_date)

    insert = """INSERT INTO tasks (title, description, assigned_to, created_by, status, priority, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    cursor.execute(insert, task_dat)

cursor.execute("SELECT * FROM users")
cursor.execute("SELECT * FROM tasks")

fetched_stuff = cursor.fetchall()

database.commit()

for row in fetched_stuff:
    print(row)

print(f"rows: {cursor.rowcount}")