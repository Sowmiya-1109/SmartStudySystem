from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
import re
import database

app = Flask(__name__)


app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart-study-secret-key"
)


def get_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

   
    if "user_id" not in session:
        return redirect("/login")

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

        elif not re.match(
            r"^[A-Za-z0-9._%+-]+@gmail\.com$",
            email
        ):
            error = "Please enter a valid Gmail address."

        elif not password:
            error = "Password should not be empty."

        elif not confirm_password:
            error = "Please confirm your password."

        elif password != confirm_password:
            error = "Passwords do not match."

        else:

            connection = get_connection()
            cursor = connection.cursor()

            try:

                cursor.execute(
                    """
                    INSERT INTO users
                    (username, email, password)
                    VALUES (%s, %s, %s)
                    """,
                    (username, email, password)
                )

                connection.commit()

            except psycopg2.errors.UniqueViolation:

                connection.rollback()

                error = "Email already registered."

                cursor.close()
                connection.close()

                return render_template(
                    "register.html",
                    error=error
                )

            cursor.close()
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

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE email = %s
            AND password = %s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:

           
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["email"] = user[2]

            return redirect("/dashboard")

        else:

            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/logout")
def logout():

    
    session.clear()

    return redirect("/login")


@app.route("/add-note", methods=["GET", "POST"])
def add_note():

    
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form["subject"]
        note_type = request.form["note_type"]
        title = request.form["title"]
        content = request.form["content"]

       
        user_id = session["user_id"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO notes
            (user_id, subject, note_type, title, content)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                subject,
                note_type,
                title,
                content
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return "Note added successfully!"

    return render_template("add_note.html")


@app.route("/notes")
def notes():

   
    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")
    subject = request.args.get("subject", "")

   
    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

   
    query = """
        SELECT id, subject, note_type, title, content
        FROM notes
        WHERE user_id = %s
    """

    values = [user_id]

    if search:

        query += """
            AND (
                title ILIKE %s
                OR content ILIKE %s
            )
        """

        values.extend([
            "%" + search + "%",
            "%" + search + "%"
        ])

    if subject:

        query += """
            AND LOWER(TRIM(subject))
            = LOWER(TRIM(%s))
        """

        values.append(subject)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)

    notes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "notes.html",
        notes=notes,
        search=search,
        subject=subject
    )


@app.route("/delete-note/<int:note_id>")
def delete_note(note_id):

    
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    
    cursor.execute(
        """
        DELETE FROM notes
        WHERE id = %s
        AND user_id = %s
        """,
        (note_id, user_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/notes")


@app.route(
    "/edit-note/<int:note_id>",
    methods=["GET", "POST"]
)
def edit_note(note_id):

    
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        subject = request.form["subject"]
        note_type = request.form["note_type"]
        title = request.form["title"]
        content = request.form["content"]

        
        cursor.execute(
            """
            UPDATE notes
            SET subject = %s,
                note_type = %s,
                title = %s,
                content = %s
            WHERE id = %s
            AND user_id = %s
            """,
            (
                subject,
                note_type,
                title,
                content,
                note_id,
                user_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/notes")

   
    cursor.execute(
        """
        SELECT id, subject, note_type, title, content
        FROM notes
        WHERE id = %s
        AND user_id = %s
        """,
        (note_id, user_id)
    )

    note = cursor.fetchone()

    cursor.close()
    connection.close()

    
    if note is None:
        return "Note not found or you do not have permission to access it."

    return render_template(
        "edit_note.html",
        note=note
    )


if __name__ == "__main__":
    app.run(debug=True)
            
