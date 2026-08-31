from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Temporary in-memory storage (Day 3-4 will make this persistent)
tasks = []
next_id = 1

@app.route("/")
def home():
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    global next_id
    task_text = request.form.get("task", "").strip()
    if task_text:
        tasks.append({
            "id": next_id,
            "text": task_text,
            "completed": False
        })
        next_id += 1
    return redirect("/")

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect("/")

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    new_text = request.form.get("new_text", "").strip()
    for task in tasks:
        if task["id"] == task_id and new_text:
            task["text"] = new_text
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
