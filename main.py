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

cursor = database.cursor()

# ** I decided to execute the commands inside of the python file itself for ease of access.

cursor.execute(
    """CREATE TABLE IF NOT EXISTS tasks(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    due_date DATE NOT NULL)"""
)
# auto_increment primary key makes sql make a new value automatically, like how an ID would work.
# not null forces sql to give a value and cant be null.

confirm = input("make new task? (Y/n) ")

if (confirm == "Y"):
    title = input("enter title: ")
    description = input("enter desc: ")
    assigned_to = input("assign to: ")
    created_by = input("who by: ")
    status = input("status: ")
    priority = input("priority: ")
    due_date = input("due date: YYYY-MM-DD ")

    insert = """INSERT INTO tasks (title, description, assigned_to, created_by, status, priority, due_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    task_dat = (title, description, assigned_to, created_by, status, priority, due_date)

    cursor.execute(insert, task_dat)

cursor.execute("SELECT * FROM tasks")
fetched_stuff = cursor.fetchall()

database.commit()

for row in fetched_stuff:
    print(row)

print(f"rows: {cursor.rowcount}")