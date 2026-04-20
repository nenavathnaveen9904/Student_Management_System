from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"  # needed for session

DB = "students.db"

# Default credentials
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ── DB INIT ──────────────────────────────────────────────
def init_db():
    """Create students table if not exists."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            branch  TEXT    NOT NULL,
            age     INTEGER NOT NULL,
            email   TEXT    NOT NULL,
            phone   TEXT    NOT NULL,
            cgpa    REAL    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ── HELPER ───────────────────────────────────────────────
def get_db():
    """Open DB connection."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn

def login_required(f):
    """Simple decorator to block unauthenticated access."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

# ── ROUTES ───────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    """Login page."""
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
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Show all students."""
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("dashboard.html", students=students)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():
    """Add a new student."""
    if request.method == "POST":
        name   = request.form["name"]
        branch = request.form["branch"]
        age    = request.form["age"]
        email  = request.form["email"]
        phone  = request.form["phone"]
        cgpa   = request.form["cgpa"]
        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, branch, age, email, phone, cgpa) VALUES (?, ?, ?, ?, ?, ?)",
            (name, branch, age, email, phone, cgpa)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return render_template("add.html")


@app.route("/update/<int:student_id>", methods=["GET", "POST"])
@login_required
def update_student(student_id):
    """Update existing student."""
    conn = get_db()
    if request.method == "POST":
        name   = request.form["name"]
        branch = request.form["branch"]
        age    = request.form["age"]
        email  = request.form["email"]
        phone  = request.form["phone"]
        cgpa   = request.form["cgpa"]
        conn.execute(
            "UPDATE students SET name=?, branch=?, age=?, email=?, phone=?, cgpa=? WHERE id=?",
            (name, branch, age, email, phone, cgpa, student_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    # GET — fetch current data to prefill form
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    return render_template("update.html", student=student)


@app.route("/delete/<int:student_id>")
@login_required
def delete_student(student_id):
    """Delete a student by ID."""
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


# ── ENTRY POINT ──────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
