@app.route("/")
def home():
    edit_id = request.args.get("edit", type=int)
    filter_by = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "none")
    search_query = request.args.get("q", "").strip().lower()

    visible_tasks = tasks

    if filter_by == "active":
        visible_tasks = [t for t in visible_tasks if not t["completed"]]
    elif filter_by == "completed":
        visible_tasks = [t for t in visible_tasks if t["completed"]]

    if search_query:
        visible_tasks = [t for t in visible_tasks if search_query in t["text"].lower() or search_query in t.get("category", "").lower()]

    if sort_by == "priority":
        visible_tasks = sorted(visible_tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority", "Medium"), 1))
    elif sort_by == "due_date":
        visible_tasks = sorted(visible_tasks, key=lambda t: t.get("due_date") or "9999-12-31")

    completed_count = len([t for t in tasks if t["completed"]])
    total_count = len(tasks)
    progress_pct = int((completed_count / total_count) * 100) if total_count > 0 else 0

    return render_template(
        "index.html",
        tasks=visible_tasks,
        edit_id=edit_id,
        filter_by=filter_by,
        sort_by=sort_by,
        search_query=search_query,
        all_tasks_count=total_count,
        completed_count=completed_count,
        progress_pct=progress_pct
    )
