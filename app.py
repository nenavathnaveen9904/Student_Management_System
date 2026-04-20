from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "secret123"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

DB_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      SERIAL PRIMARY KEY,
            name    TEXT NOT NULL,
            branch  TEXT NOT NULL,
            age     INTEGER NOT NULL,
            email   TEXT NOT NULL,
            phone   TEXT NOT NULL,
            cgpa    REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials. Try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", students=students)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name   = request.form["name"]
        branch = request.form["branch"]
        age    = request.form["age"]
        email  = request.form["email"]
        phone  = request.form["phone"]
        cgpa   = request.form["cgpa"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (name, branch, age, email, phone, cgpa) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, branch, age, email, phone, cgpa)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return render_template("add.html")

@app.route("/update/<int:student_id>", methods=["GET", "POST"])
@login_required
def update_student(student_id):
    conn = get_db()
    if request.method == "POST":
        name   = request.form["name"]
        branch = request.form["branch"]
        age    = request.form["age"]
        email  = request.form["email"]
        phone  = request.form["phone"]
        cgpa   = request.form["cgpa"]
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET name=%s, branch=%s, age=%s, email=%s, phone=%s, cgpa=%s WHERE id=%s",
            (name, branch, age, email, phone, cgpa, student_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    student = cur.fetchone()
    conn.close()
    return render_template("update.html", student=student)

@app.route("/delete/<int:student_id>")
@login_required
def delete_student(student_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)