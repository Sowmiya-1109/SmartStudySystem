from flask import Flask, render_template,request, redirect
import sqlite3
import re
import database

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username:
            error = "Name should not be empty."

        elif not email:
            error = "Email should not be empty."

        elif not re.match(r"^[A-Za-z0-9._%+-]+@gmail\.com$", email):
            error = "Please enter a valid Gmail address."

        elif not password:
            error = "Password should not be empty."

        elif not confirm_password:
            error = "Please confirm your password."

        elif password != confirm_password:
            error = "Passwords do not match."

        else:
            connection = sqlite3.connect(
                "study_material.db",
                timeout=10
            )

            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )

            connection.commit()
            connection.close()

            return redirect("/login")

    return render_template(
        "register.html",
        error=error
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = sqlite3.connect("study_material.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()

        connection.close()

        if user:
            return render_template("dashboard.html")
        else:
            return "Invalid email or password!"

    return render_template("login.html")

@app.route("/add-note", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        subject = request.form["subject"]
        note_type = request.form["note_type"]
        title = request.form["title"]
        content = request.form["content"]

        connection = sqlite3.connect("study_material.db")
        cursor = connection.cursor()

        cursor.execute(
    "INSERT INTO notes (subject, note_type, title, content) VALUES (?, ?, ?, ?)",
    (subject, note_type, title, content)
)

        connection.commit()
        connection.close()

        return "Note added successfully!"

    return render_template("add_note.html")

@app.route("/notes")
def notes():
    search = request.args.get("search", "")
    subject = request.args.get("subject", "")

    connection = sqlite3.connect("study_material.db")
    cursor = connection.cursor()

    query = "SELECT * FROM notes WHERE 1=1"
    values = []

    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        values.extend([
            "%" + search + "%",
            "%" + search + "%"
        ])

    if subject:
        query += " AND subject = ?"
        values.append(subject)

    cursor.execute(query, values)

    notes = cursor.fetchall()

    connection.close()

    return render_template(
        "notes.html",
        notes=notes,
        search=search,
        subject=subject
    )

@app.route("/delete-note/<int:note_id>")
def delete_note(note_id):
    connection = sqlite3.connect("study_material.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/notes")


@app.route("/edit-note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    connection = sqlite3.connect("study_material.db")
    cursor = connection.cursor()

    if request.method == "POST":
        subject = request.form["subject"]
        note_type = request.form["note_type"]
        title = request.form["title"]
        content = request.form["content"]

        cursor.execute(
            "UPDATE notes SET subject = ?, note_type = ?, title = ?, content = ? WHERE id = ?",
            (subject, note_type, title, content, note_id)
        )

        connection.commit()
        connection.close()

        return redirect("/notes")

    cursor.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    )

    note = cursor.fetchone()

    connection.close()

    return render_template("edit_note.html", note=note)

if __name__ == "__main__":
    app.run(debug=True)
   

        
   
