from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "todo_secret_key"

init_db()

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


# ---------- Auth ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        else:
            conn = get_connection()
            existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                error = "That username is already taken."
            else:
                hashed = generate_password_hash(password)
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
                conn.commit()
                user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
                session["user_id"] = user["id"]
                session["username"] = username
                conn.close()
                return redirect("/")
            conn.close()

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- Main App ----------

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    edit_id = request.args.get("edit", type=int)
    filter_by = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "none")
    search_query = request.args.get("q", "").strip().lower()

    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)).fetchall()
    conn.close()

    tasks = [dict(row) for row in rows]

    if filter_by == "active":
        tasks = [t for t in tasks if not t["completed"]]
    elif filter_by == "completed":
        tasks = [t for t in tasks if t["completed"]]

    if search_query:
        tasks = [t for t in tasks if search_query in t["text"].lower() or search_query in (t["category"] or "").lower()]

    if sort_by == "priority":
        tasks = sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t["priority"], 1))
    elif sort_by == "due_date":
        tasks = sorted(tasks, key=lambda t: t["due_date"] or "9999-12-31")

    all_tasks_count = len(rows)
    completed_count = len([t for t in rows if t["completed"]])
    progress_pct = int((completed_count / all_tasks_count) * 100) if all_tasks_count > 0 else 0

    return render_template(
        "index.html",
        tasks=tasks,
        edit_id=edit_id,
        filter_by=filter_by,
        sort_by=sort_by,
        search_query=search_query,
        all_tasks_count=all_tasks_count,
        completed_count=completed_count,
        progress_pct=progress_pct,
        username=session.get("username")
    )


@app.route("/add", methods=["POST"])
def add_task():
    task_text = request.form.get("task", "").strip()
    category = request.form.get("category", "General").strip() or "General"
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")

    if task_text:
        conn = get_connection()
        existing = conn.execute(
            "SELECT id FROM tasks WHERE user_id = ? AND LOWER(text) = ?",
            (session["user_id"], task_text.lower())
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO tasks (user_id, text, category, priority, due_date) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], task_text, category, priority, due_date)
            )
            conn.commit()
        conn.close()
    return redirect("/")


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_connection()
    task = conn.execute("SELECT completed FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])).fetchone()
    if task:
        new_status = 0 if task["completed"] else 1
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_text = request.form.get("new_text", "").strip()
    new_category = request.form.get("new_category", "General").strip() or "General"
    new_priority = request.form.get("new_priority", "Medium")
    new_due_date = request.form.get("new_due_date", "")

    if new_text:
        conn = get_connection()
        conn.execute(
            "UPDATE tasks SET text=?, category=?, priority=?, due_date=? WHERE id=? AND user_id=?",
            (new_text, new_category, new_priority, new_due_date, task_id, session["user_id"])
        )
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/clear_completed")
def clear_completed():
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE user_id = ? AND completed = 1", (session["user_id"],))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
