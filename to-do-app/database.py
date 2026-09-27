import sqlite3
from datetime import datetime, timedelta

DB_FILE = "todo.db"


def get_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT DEFAULT '',
            completed INTEGER DEFAULT 0,
            recurrence TEXT DEFAULT 'none',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            collaborator_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id),
            FOREIGN KEY (collaborator_id) REFERENCES users (id),
            UNIQUE(owner_id, collaborator_id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- Task queries ----------

def get_tasks_for_user(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    tasks = [dict(row) for row in rows]
    conn.close()

    for task in tasks:
        task["subtasks"] = get_subtasks_for_task(task["id"])

    return tasks


def get_task_by_id_any_owner(task_id):
    """Fetch a task regardless of owner — used when checking share permissions."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_task_by_id(user_id, task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def task_exists(user_id, text):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM tasks WHERE user_id = ? AND LOWER(text) = ?",
        (user_id, text.lower())
    ).fetchone()
    conn.close()
    return row is not None


def insert_task(user_id, text, category, priority, due_date, recurrence="none"):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (user_id, text, category, priority, due_date, recurrence) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, text, category, priority, due_date, recurrence)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def toggle_task_complete_any_owner(task_id):
    """Toggle completion regardless of owner — permission is checked by caller via share access."""
    conn = get_connection()
    task = conn.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task:
        new_status = 0 if task["completed"] else 1
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
    conn.close()


def toggle_task_complete(user_id, task_id):
    conn = get_connection()
    task = conn.execute("SELECT completed FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id)).fetchone()
    if task:
        new_status = 0 if task["completed"] else 1
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
    conn.close()


def delete_task_by_id(user_id, task_id):
    conn = get_connection()
    conn.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()


def update_task(user_id, task_id, text, category, priority, due_date):
    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET text=?, category=?, priority=?, due_date=? WHERE id=? AND user_id=?",
        (text, category, priority, due_date, task_id, user_id)
    )
    conn.commit()
    conn.close()


def delete_completed_tasks(user_id):
    conn = get_connection()
    completed_ids = conn.execute(
        "SELECT id FROM tasks WHERE user_id = ? AND completed = 1", (user_id,)
    ).fetchall()
    for row in completed_ids:
        conn.execute("DELETE FROM subtasks WHERE task_id = ?", (row["id"],))
    conn.execute("DELETE FROM tasks WHERE user_id = ? AND completed = 1", (user_id,))
    conn.commit()
    conn.close()


def calculate_next_due_date(current_due_date, recurrence):
    if not current_due_date:
        base_date = datetime.now()
    else:
        try:
            base_date = datetime.strptime(current_due_date, "%Y-%m-%d")
        except ValueError:
            base_date = datetime.now()

    if recurrence == "daily":
        next_date = base_date + timedelta(days=1)
    elif recurrence == "weekly":
        next_date = base_date + timedelta(weeks=1)
    else:
        return current_due_date

    return next_date.strftime("%Y-%m-%d")


def get_due_and_overdue_tasks(user_id):
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND completed = 0 AND due_date != ''",
        (user_id,)
    ).fetchall()
    conn.close()

    tasks = [dict(row) for row in rows]
    overdue = [t for t in tasks if t["due_date"] < today_str]
    due_today = [t for t in tasks if t["due_date"] == today_str]

    return overdue, due_today


# ---------- Subtask queries ----------

def get_subtasks_for_task(task_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM subtasks WHERE task_id = ?", (task_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_subtask(task_id, text):
    conn = get_connection()
    conn.execute("INSERT INTO subtasks (task_id, text) VALUES (?, ?)", (task_id, text))
    conn.commit()
    conn.close()


def toggle_subtask_complete(subtask_id):
    conn = get_connection()
    row = conn.execute("SELECT completed FROM subtasks WHERE id = ?", (subtask_id,)).fetchone()
    if row:
        new_status = 0 if row["completed"] else 1
        conn.execute("UPDATE subtasks SET completed = ? WHERE id = ?", (new_status, subtask_id))
        conn.commit()
    conn.close()


def delete_subtask(subtask_id):
    conn = get_connection()
    conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()
    conn.close()


# ---------- User queries ----------

def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def create_user(username, hashed_password):
    conn = get_connection()
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return get_user_by_username(username)


# ---------- Sharing queries ----------

def share_list_with(owner_id, collaborator_username):
    """Returns 'ok', 'not_found', 'self', or 'already_shared'."""
    collaborator = get_user_by_username(collaborator_username)
    if not collaborator:
        return "not_found"
    if collaborator["id"] == owner_id:
        return "self"

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM shares WHERE owner_id = ? AND collaborator_id = ?",
        (owner_id, collaborator["id"])
    ).fetchone()
    if existing:
        conn.close()
        return "already_shared"

    conn.execute(
        "INSERT INTO shares (owner_id, collaborator_id) VALUES (?, ?)",
        (owner_id, collaborator["id"])
    )
    conn.commit()
    conn.close()
    return "ok"


def remove_share(owner_id, collaborator_id):
    conn = get_connection()
    conn.execute("DELETE FROM shares WHERE owner_id = ? AND collaborator_id = ?", (owner_id, collaborator_id))
    conn.commit()
    conn.close()


def get_lists_shared_with_me(user_id):
    """Return list of {owner_id, username} for lists shared with this user."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT users.id AS owner_id, users.username AS username
        FROM shares
        JOIN users ON users.id = shares.owner_id
        WHERE shares.collaborator_id = ?
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_my_collaborators(owner_id):
    """Return list of {collaborator_id, username} for people I've shared my list with."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT users.id AS collaborator_id, users.username AS username
        FROM shares
        JOIN users ON users.id = shares.collaborator_id
        WHERE shares.owner_id = ?
    """, (owner_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def has_access_to_list(viewer_id, owner_id):
    """True if viewer_id is the owner, or the owner has shared their list with viewer_id."""
    if viewer_id == owner_id:
        return True
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM shares WHERE owner_id = ? AND collaborator_id = ?",
        (owner_id, viewer_id)
    ).fetchone()
    conn.close()
    return row is not None
