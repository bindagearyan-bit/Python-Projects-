import sqlite3

DB_FILE = "todo.db"


def get_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users and tasks tables if they don't already exist."""
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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


# ---------- Task queries (used by app.py) ----------

def get_tasks_for_user(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def task_exists(user_id, text):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM tasks WHERE user_id = ? AND LOWER(text) = ?",
        (user_id, text.lower())
    ).fetchone()
    conn.close()
    return row is not None


def insert_task(user_id, text, category, priority, due_date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, text, category, priority, due_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, text, category, priority, due_date)
    )
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
    conn.execute("DELETE FROM tasks WHERE user_id = ? AND completed = 1", (user_id,))
    conn.commit()
    conn.close()


# ---------- User queries ----------

def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def create_user(username, hashed_password):
    conn = get_connection()
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return get_user_by_username(username)