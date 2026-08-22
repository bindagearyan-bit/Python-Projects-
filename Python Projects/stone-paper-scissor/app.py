import os
import json
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
import random
from rps_terminal import check
from collections import Counter

app = Flask(__name__)
app.secret_key = "rps_secret_key"
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

def load_leaderboard():
    """Load leaderboard data from leaderboard.json safely."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("matches", [])
                    data.setdefault("best_streak", 0)
                    return data
        except Exception:
            pass
    return {"matches": [], "best_streak": 0}

def save_leaderboard(data):
    """Save leaderboard data to leaderboard.json."""
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving leaderboard: {e}")

def record_match(player, opponent, result_str, mode, streak):
    """Record completed match and update overall best streak."""
    data = load_leaderboard()
    match_entry = {
        "player": player,
        "opponent": opponent,
        "result": result_str,
        "mode": mode,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data["matches"].insert(0, match_entry)
    data["best_streak"] = max(data.get("best_streak", 0), streak)
    save_leaderboard(data)

def update_alltime_best_streak(current_streak):
    """Update all-time best streak in leaderboard file if current exceeds it."""
    if current_streak <= 0:
        return
    data = load_leaderboard()
    if current_streak > data.get("best_streak", 0):
        data["best_streak"] = current_streak
        save_leaderboard(data)

def get_smart_computer_choice(history):
    if len(history) < 3:
        return random.choice(["rock", "paper", "scissor"])
    most_common = Counter(history).most_common(1)[0][0]
    counter_move = {"rock": "paper", "paper": "scissor", "scissor": "rock"}
    return counter_move[most_common]

def init_session():
    """Ensure all required session variables are initialized with default values."""
    session.setdefault("started", False)
    session.setdefault("wins", 0)
    session.setdefault("losses", 0)
    session.setdefault("draws", 0)
    session.setdefault("round", 0)
    session.setdefault("total_rounds", 3)
    session.setdefault("game_mode", "computer")
    session.setdefault("difficulty", "easy")
    session.setdefault("history", [])
    session.setdefault("p1_choice", None)
    session.setdefault("theme", "light")
    session.setdefault("p1_name", session.get("name", "Player 1"))
    session.setdefault("p2_name", "Player 2")
    session.setdefault("streak", 0)
    session.setdefault("match_saved", False)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "name" in request.form:
        name = request.form.get("name", "").strip()
        if name:
            session["name"] = name
            session["p1_name"] = name
            session["theme"] = session.get("theme", "light")
            init_session()
            return redirect(url_for("game"))
    elif "name" in session:
        return redirect(url_for("game"))

    return render_template("login.html", active_page="login", theme=session.get("theme", "light"))

@app.route("/game", methods=["GET", "POST"])
def game():
    if "name" not in session:
        return redirect(url_for("login"))

    init_session()

    result = None
    user_choice = None
    comp_choice = None
    match_over = False
    match_result = None
    waiting_p2 = False

    if request.method == "POST":
        if "update_names" in request.form or "p2name" in request.form:
            p1 = request.form.get("p1_name", request.form.get("name", "")).strip()
            p2 = request.form.get("p2_name", request.form.get("p2name", "")).strip()
            if p1:
                session["p1_name"] = p1
                session["name"] = p1
            if p2:
                session["p2_name"] = p2

        elif "mode" in request.form:
            session["total_rounds"] = int(request.form["mode"])
            session["wins"] = 0
            session["losses"] = 0
            session["draws"] = 0
            session["round"] = 0
            session["history"] = []
            session["started"] = True
            session["match_saved"] = False

        elif "game_mode" in request.form:
            session["game_mode"] = request.form["game_mode"]
            if session["game_mode"] == "2player" and not session.get("p2_name"):
                session["p2_name"] = "Player 2"

        elif "difficulty" in request.form:
            session["difficulty"] = request.form["difficulty"]

        elif "theme" in request.form:
            session["theme"] = request.form["theme"]

        elif "choice" in request.form:
            user_choice = request.form["choice"]
            p1_name = session.get("p1_name", session.get("name", "Player 1"))
            p2_name = session.get("p2_name", "Player 2")

            if session.get("game_mode") == "2player":
                if session.get("p1_choice") is None:
                    session["p1_choice"] = user_choice
                    waiting_p2 = True
                else:
                    p1 = session["p1_choice"]
                    p2 = user_choice
                    score = check(p1, p2)
                    user_choice = f"{p1_name}: {p1.capitalize()}"
                    comp_choice = f"{p2_name}: {p2.capitalize()}"
                    session["p1_choice"] = None

                    if score == 0:
                        result = "It's a draw!"
                        session["draws"] = session.get("draws", 0) + 1
                    elif score == 1:
                        result = f"{p1_name} Wins!"
                        session["wins"] = session.get("wins", 0) + 1
                        session["streak"] = session.get("streak", 0) + 1
                    else:
                        result = f"{p2_name} Wins!"
                        session["losses"] = session.get("losses", 0) + 1
                        session["streak"] = 0

                    session["round"] = session.get("round", 0) + 1
            else:
                choices = ["rock", "paper", "scissor"]
                if session.get("difficulty") == "hard":
                    comp_choice = get_smart_computer_choice(session.get("history", []))
                else:
                    comp_choice = random.choice(choices)

                history = list(session.get("history", []))
                history.append(user_choice)
                session["history"] = history

                score = check(comp_choice, user_choice)

                if score == 0:
                    result = "It's a draw!"
                    session["draws"] = session.get("draws", 0) + 1
                elif score == 1:
                    result = "You Win!"
                    session["wins"] = session.get("wins", 0) + 1
                    session["streak"] = session.get("streak", 0) + 1
                else:
                    result = "You Lose!"
                    session["losses"] = session.get("losses", 0) + 1
                    session["streak"] = 0

                session["round"] = session.get("round", 0) + 1

            # Update all-time best streak in json
            update_alltime_best_streak(session.get("streak", 0))

            if session.get("round", 0) >= session.get("total_rounds", 3):
                match_over = True
                wins = session.get("wins", 0)
                losses = session.get("losses", 0)
                if session.get("game_mode") == "2player":
                    if wins > losses:
                        match_result = f"{p1_name} won the match! 🎉"
                        res_summary = f"{p1_name} Won ({wins}-{losses})"
                    elif losses > wins:
                        match_result = f"{p2_name} won the match! 🎉"
                        res_summary = f"{p2_name} Won ({losses}-{wins})"
                    else:
                        match_result = "The match is a draw!"
                        res_summary = f"Draw ({wins}-{losses})"
                    opponent = p2_name
                else:
                    diff = session.get("difficulty", "easy").capitalize()
                    opponent = f"Computer ({diff})"
                    if wins > losses:
                        match_result = "You won the match! 🎉"
                        res_summary = f"Won ({wins}-{losses})"
                    elif losses > wins:
                        match_result = "You lost the match!"
                        res_summary = f"Lost ({wins}-{losses})"
                    else:
                        match_result = "The match is a draw!"
                        res_summary = f"Draw ({wins}-{losses})"

                if not session.get("match_saved"):
                    mode_text = f"Best of {session.get('total_rounds', 3)}"
                    player_name = session.get("p1_name", session.get("name", "Player 1"))
                    record_match(player_name, opponent, res_summary, mode_text, session.get("streak", 0))
                    session["match_saved"] = True

    return render_template(
        "index.html",
        active_page="game",
        name=session.get("name"),
        p1_name=session.get("p1_name", session.get("name", "Player 1")),
        p2_name=session.get("p2_name", "Player 2"),
        theme=session.get("theme", "light"),
        game_mode=session.get("game_mode", "computer"),
        difficulty=session.get("difficulty", "easy"),
        result=result,
        user_choice=user_choice,
        comp_choice=comp_choice,
        wins=session.get("wins", 0),
        losses=session.get("losses", 0),
        draws=session.get("draws", 0),
        round=session.get("round", 0),
        total_rounds=session.get("total_rounds", 3),
        match_over=match_over,
        match_result=match_result,
        started=session.get("started", False),
        waiting_p2=waiting_p2,
        streak=session.get("streak", 0)
    )

@app.route("/rules")
def rules():
    init_session()
    return render_template(
        "rules.html",
        active_page="rules",
        theme=session.get("theme", "light"),
        name=session.get("name")
    )

@app.route("/leaderboard")
def leaderboard():
    init_session()
    data = load_leaderboard()
    matches = data.get("matches", [])[:10]
    best_streak = max(data.get("best_streak", 0), session.get("streak", 0))
    return render_template(
        "leaderboard.html",
        active_page="leaderboard",
        theme=session.get("theme", "light"),
        matches=matches,
        best_streak=best_streak,
        current_streak=session.get("streak", 0),
        name=session.get("name")
    )

@app.route("/reset")
def reset():
    name = session.get("name")
    p1_name = session.get("p1_name")
    p2_name = session.get("p2_name")
    theme = session.get("theme", "light")
    game_mode = session.get("game_mode", "computer")
    difficulty = session.get("difficulty", "easy")
    streak = session.get("streak", 0)
    session.clear()
    if name:
        session["name"] = name
        session["p1_name"] = p1_name or name
        session["p2_name"] = p2_name or "Player 2"
        session["theme"] = theme
        session["game_mode"] = game_mode
        session["difficulty"] = difficulty
        session["streak"] = streak
        init_session()
    return redirect(url_for("game"))

if __name__ == "__main__":
    app.run(debug=True)
