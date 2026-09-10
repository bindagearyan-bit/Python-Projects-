# 📝 To-Do List App

A full-featured to-do list web app built with Python + Flask, with real user accounts, categories, priorities, due dates, and search — backed by SQLite.

## 📌 About

Started as a simple add/view/complete/delete task list and grew into a multi-user productivity app with persistent storage, filtering, sorting, search, and a progress tracker.

## 🚀 Features

- **User accounts** — sign up / log in with hashed passwords, each user has a private task list
- **Add, edit, complete, and delete tasks**
- **Categories** — organize tasks (Work, Personal, Study, etc.)
- **Priority levels** — High / Medium / Low, color-coded
- **Due dates** — date picker per task
- **Filter** — All / Active / Completed
- **Sort** — by Priority or Due Date
- **Search** — find tasks by text or category
- **Progress bar** — visual completion tracker
- **Clear Completed** — remove all finished tasks in one click
- Persistent storage via **SQLite** — tasks survive restarts and are private per user

## 🛠️ Tech Stack

- Python 3
- Flask
- SQLite (via Python's built-in `sqlite3`)
- Werkzeug (password hashing)

## 📁 Project Structure

```
todo-app/
├── app.py           # Flask routes and request handling
├── database.py      # All database queries (users + tasks)
├── requirements.txt
├── todo.db          # SQLite database (not committed — see .gitignore)
└── templates/
    ├── login.html
    ├── signup.html
    └── index.html
```

## ▶️ How to Run

```bash
git clone <your-repo-link>
cd todo-app
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`, sign up for an account, and start adding tasks.

## 🗺️ Roadmap / Upcoming Features

- [ ] Dark / light mode toggle
- [ ] Subtasks / checklists within a task
- [ ] Recurring tasks (daily/weekly)
- [ ] Reminders/notifications
- [ ] Calendar view
- [ ] Shareable/collaborative lists
- [ ] Deploy live + package as an installable app

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are always welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
