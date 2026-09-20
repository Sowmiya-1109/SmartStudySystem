import sqlite3

connection = sqlite3.connect("study_material.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    note_type NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
)
""")


connection.commit()
connection.close()

print("Database and users table created successfully!")
