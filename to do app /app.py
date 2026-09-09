from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import database as db

app = Flask(__name__)
app.secret_key = "todo_secret_key"

db.init_db()

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def require_login():
    """Return True if a user is logged in, else False."""
    return "user_id" in session


# ---------- Auth ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        elif db.get_user_by_username(username):
            error = "That username is already taken."
        else:
            hashed = generate_password_hash(password)
            user = db.create_user(username, hashed)
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect("/")

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_username(username)

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
    if not require_login():
        return redirect("/login")

    edit_id = request.args.get("edit", type=int)
    filter_by = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "none")
    search_query = request.args.get("q", "").strip().lower()

    all_tasks = db.get_tasks_for_user(session["user_id"])
    tasks = filter_and_sort_tasks(all_tasks, filter_by, sort_by, search_query)

    all_tasks_count = len(all_tasks)
    completed_count = len([t for t in all_tasks if t["completed"]])
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


def filter_and_sort_tasks(tasks, filter_by, sort_by, search_query):
    """Apply status filter, text search, and sort order to a task list."""
    if filter_by == "active":
        tasks = [t for t in tasks if not t["completed"]]
    elif filter_by == "completed":
        tasks = [t for t in tasks if t["completed"]]

    if search_query:
        tasks = [
            t for t in tasks
            if search_query in t["text"].lower() or search_query in (t["category"] or "").lower()
        ]

    if sort_by == "priority":
        tasks = sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t["priority"], 1))
    elif sort_by == "due_date":
        tasks = sorted(tasks, key=lambda t: t["due_date"] or "9999-12-31")

    return tasks


@app.route("/add", methods=["POST"])
def add_task():
    task_text = request.form.get("task", "").strip()
    category = request.form.get("category", "General").strip() or "General"
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")

    if task_text and not db.task_exists(session["user_id"], task_text):
        db.insert_task(session["user_id"], task_text, category, priority, due_date)

    return redirect("/")


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    db.toggle_task_complete(session["user_id"], task_id)
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    db.delete_task_by_id(session["user_id"], task_id)
    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_text = request.form.get("new_text", "").strip()
    new_category = request.form.get("new_category", "General").strip() or "General"
    new_priority = request.form.get("new_priority", "Medium")
    new_due_date = request.form.get("new_due_date", "")

    if new_text:
        db.update_task(session["user_id"], task_id, new_text, new_category, new_priority, new_due_date)

    return redirect("/")


@app.route("/clear_completed")
def clear_completed():
    db.delete_completed_tasks(session["user_id"])
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)