from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

tasks = load_tasks()
next_id = max([t["id"] for t in tasks], default=0) + 1

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

@app.route("/")
def home():
    edit_id = request.args.get("edit", type=int)
    filter_by = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "none")

    visible_tasks = tasks

    if filter_by == "active":
        visible_tasks = [t for t in visible_tasks if not t["completed"]]
    elif filter_by == "completed":
        visible_tasks = [t for t in visible_tasks if t["completed"]]

    if sort_by == "priority":
        visible_tasks = sorted(visible_tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority", "Medium"), 1))
    elif sort_by == "due_date":
        visible_tasks = sorted(visible_tasks, key=lambda t: t.get("due_date") or "9999-12-31")

    return render_template(
        "index.html",
        tasks=visible_tasks,
        edit_id=edit_id,
        filter_by=filter_by,
        sort_by=sort_by,
        all_tasks_count=len(tasks)
    )

@app.route("/add", methods=["POST"])
def add_task():
    global next_id
    task_text = request.form.get("task", "").strip()
    category = request.form.get("category", "General").strip() or "General"
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")

    if task_text and not any(t["text"].lower() == task_text.lower() for t in tasks):
        tasks.append({
            "id": next_id,
            "text": task_text,
            "completed": False,
            "category": category,
            "priority": priority,
            "due_date": due_date
        })
        next_id += 1
        save_tasks(tasks)
    return redirect("/")

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
    save_tasks(tasks)
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return redirect("/")

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_text = request.form.get("new_text", "").strip()
    new_category = request.form.get("new_category", "General").strip() or "General"
    new_priority = request.form.get("new_priority", "Medium")
    new_due_date = request.form.get("new_due_date", "")

    for task in tasks:
        if task["id"] == task_id and new_text:
            task["text"] = new_text
            task["category"] = new_category
            task["priority"] = new_priority
            task["due_date"] = new_due_date
    save_tasks(tasks)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
