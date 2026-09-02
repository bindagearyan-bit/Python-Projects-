from flask import Flask, render_template, request, redirect
import json
import os

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

@app.route("/")
def home():
    edit_id = request.args.get("edit", type=int)
    return render_template("index.html", tasks=tasks, edit_id=edit_id)

@app.route("/add", methods=["POST"])
def add_task():
    global next_id
    task_text = request.form.get("task", "").strip()
    if task_text and not any(t["text"].lower() == task_text.lower() for t in tasks):
        tasks.append({
            "id": next_id,
            "text": task_text,
            "completed": False
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
    for task in tasks:
        if task["id"] == task_id and new_text:
            task["text"] = new_text
    save_tasks(tasks)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
