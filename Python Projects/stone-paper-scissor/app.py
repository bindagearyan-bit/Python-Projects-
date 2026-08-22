import os
import json
import uuid
import random
from datetime import datetime
from collections import Counter
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "rps_match_ticket_secret_key"

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

# In-memory storage for online multiplayer rooms
ROOMS = {}

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

def record_match(player, opponent, result_str, mode, streak=0):
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
    data["matches"] = data["matches"][:10]  # Keep last 10 matches
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

def check_winner(move1, move2):
    """
    Returns 0 if draw, 1 if move1 wins, 2 if move2 wins.
    """
    m1 = move1.lower()
    m2 = move2.lower()
    if m1 == m2:
        return 0
    if (m1 == "rock" and m2 == "scissor") or \
       (m1 == "scissor" and m2 == "paper") or \
       (m1 == "paper" and m2 == "rock"):
        return 1
    return 2

def get_smart_computer_choice(history):
    if len(history) < 3:
        return random.choice(["rock", "paper", "scissor"])
    most_common = Counter(history).most_common(1)[0][0]
    counter_move = {"rock": "paper", "paper": "scissor", "scissor": "rock"}
    return counter_move.get(most_common, random.choice(["rock", "paper", "scissor"]))

def init_session():
    """Ensure all required session variables are initialized with default values."""
    if "player_id" not in session:
        session["player_id"] = uuid.uuid4().hex
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
        if "p2name" in request.form:
            p2 = request.form.get("p2name", "").strip()
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
                    outcome = check_winner(p1, p2)
                    user_choice = f"{p1_name}: {p1.capitalize()}"
                    comp_choice = f"{p2_name}: {p2.capitalize()}"
                    session["p1_choice"] = None

                    if outcome == 0:
                        result = "It's a draw!"
                        session["draws"] = session.get("draws", 0) + 1
                    elif outcome == 1:
                        result = f"{p1_name} Wins!"
                        session["wins"] = session.get("wins", 0) + 1
                    else:
                        result = f"{p2_name} Wins!"
                        session["losses"] = session.get("losses", 0) + 1

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

                outcome = check_winner(user_choice, comp_choice)

                if outcome == 0:
                    result = "It's a draw!"
                    session["draws"] = session.get("draws", 0) + 1
                elif outcome == 1:
                    result = "You Win!"
                    session["wins"] = session.get("wins", 0) + 1
                    session["streak"] = session.get("streak", 0) + 1
                else:
                    result = "You Lose!"
                    session["losses"] = session.get("losses", 0) + 1
                    session["streak"] = 0

                session["round"] = session.get("round", 0) + 1

            if session.get("game_mode") == "computer":
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
                    record_match(player_name, opponent, res_summary, mode_text, session.get("streak", 0) if session.get("game_mode") == "computer" else 0)
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

@app.route("/about")
def about():
    init_session()
    return render_template(
        "about.html",
        active_page="about",
        theme=session.get("theme", "light"),
        name=session.get("name")
    )

def get_heatmap_data(matches):
    """Generate 35 days of activity data (5 weeks x 7 days) for commit/activity heatmap."""
    today = datetime.now().date()
    counts = {}
    for m in matches:
        date_str = m.get("date", "")
        if date_str:
            try:
                dt = datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d").date()
                counts[dt] = counts.get(dt, 0) + 1
            except Exception:
                pass

    heatmap_days = []
    for i in range(34, -1, -1):
        day = today - timedelta(days=i)
        cnt = counts.get(day, 0)
        if cnt == 0:
            level = 0
        elif cnt <= 2:
            level = 1
        elif cnt <= 4:
            level = 2
        elif cnt <= 6:
            level = 3
        else:
            level = 4

        heatmap_days.append({
            "date": day.strftime("%b %d"),
            "count": cnt,
            "level": level
        })
    return heatmap_days

@app.route("/leaderboard")
def leaderboard():
    init_session()
    data = load_leaderboard()
    all_matches = data.get("matches", [])
    matches = all_matches[:10]
    best_streak = max(data.get("best_streak", 0), session.get("streak", 0))
    heatmap_days = get_heatmap_data(all_matches)
    return render_template(
        "leaderboard.html",
        active_page="leaderboard",
        theme=session.get("theme", "light"),
        matches=matches,
        best_streak=best_streak,
        current_streak=session.get("streak", 0),
        heatmap_days=heatmap_days,
        name=session.get("name")
    )

@app.route("/online", methods=["GET", "POST"])
def online():
    if "name" not in session:
        return redirect(url_for("login"))
    init_session()

    error = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            total_rounds = int(request.form.get("total_rounds", 3))
            room_code = f"TKT-{random.randint(1000, 9999)}"
            ROOMS[room_code] = {
                "code": room_code,
                "p1_name": session.get("name", "Player 1"),
                "p1_id": session.get("player_id"),
                "p2_name": None,
                "p2_id": None,
                "total_rounds": total_rounds,
                "p1_score": 0,
                "p2_score": 0,
                "draws": 0,
                "round": 0,
                "p1_choice": None,
                "p2_choice": None,
                "round_result": None,
                "match_over": False,
                "match_result": None,
                "match_saved": False
            }
            return redirect(url_for("room", code=room_code))

        elif action == "join":
            room_code = request.form.get("room_code", "").strip().upper()
            if room_code in ROOMS:
                room = ROOMS[room_code]
                pid = session.get("player_id")
                if room["p1_id"] != pid and room["p2_id"] is None:
                    room["p2_name"] = session.get("name", "Player 2")
                    room["p2_id"] = pid
                return redirect(url_for("room", code=room_code))
            else:
                error = f"Room code '{room_code}' not found!"

    return render_template(
        "online.html",
        active_page="online",
        theme=session.get("theme", "light"),
        name=session.get("name"),
        active_rooms=ROOMS,
        error=error
    )

@app.route("/room/<code>", methods=["GET", "POST"])
def room(code):
    if "name" not in session:
        return redirect(url_for("login"))
    init_session()

    code = code.upper()
    if code not in ROOMS:
        return redirect(url_for("online"))

    room_data = ROOMS[code]
    pid = session.get("player_id")

    # Join as P2 if room missing P2 and current player is not P1
    if room_data["p1_id"] != pid and room_data["p2_id"] is None:
        room_data["p2_name"] = session.get("name", "Player 2")
        room_data["p2_id"] = pid

    is_p1 = (room_data["p1_id"] == pid)
    is_p2 = (room_data["p2_id"] == pid)

    if request.method == "POST" and not room_data["match_over"]:
        choice = request.form.get("choice")
        if choice in ["rock", "paper", "scissor"]:
            if is_p1:
                room_data["p1_choice"] = choice
            elif is_p2:
                room_data["p2_choice"] = choice

            # If both players submitted choices, resolve round
            if room_data["p1_choice"] and room_data["p2_choice"]:
                p1_c = room_data["p1_choice"]
                p2_c = room_data["p2_choice"]
                outcome = check_winner(p1_c, p2_c)

                if outcome == 0:
                    room_data["round_result"] = "It's a Draw!"
                    room_data["draws"] += 1
                elif outcome == 1:
                    room_data["round_result"] = f"{room_data['p1_name']} (P1) Wins Round!"
                    room_data["p1_score"] += 1
                else:
                    room_data["round_result"] = f"{room_data['p2_name']} (P2) Wins Round!"
                    room_data["p2_score"] += 1

                room_data["round"] += 1

                if room_data["round"] >= room_data["total_rounds"]:
                    room_data["match_over"] = True
                    p1_s = room_data["p1_score"]
                    p2_s = room_data["p2_score"]
                    if p1_s > p2_s:
                        room_data["match_result"] = f"{room_data['p1_name']} Won Match! 🎉"
                        summary = f"{room_data['p1_name']} Won ({p1_s}-{p2_s})"
                    elif p2_s > p1_s:
                        room_data["match_result"] = f"{room_data['p2_name']} Won Match! 🎉"
                        summary = f"{room_data['p2_name']} Won ({p2_s}-{p1_s})"
                    else:
                        room_data["match_result"] = "Match ended in a Draw!"
                        summary = f"Draw ({p1_s}-{p2_s})"

                    if not room_data.get("match_saved"):
                        record_match(
                            room_data["p1_name"],
                            f"{room_data['p2_name']} (Online)",
                            summary,
                            f"Online Best of {room_data['total_rounds']}"
                        )
                        room_data["match_saved"] = True

    # Determine auto-polling status (every 2s)
    should_poll = False
    if not room_data["p2_name"]:
        should_poll = True
    elif not room_data["match_over"]:
        if is_p1 and room_data["p1_choice"] and not room_data["p2_choice"]:
            should_poll = True
        elif is_p2 and room_data["p2_choice"] and not room_data["p1_choice"]:
            should_poll = True
        elif room_data["p1_choice"] and room_data["p2_choice"]:
            should_poll = True
        elif not (is_p1 or is_p2):
            should_poll = True

    return render_template(
        "room.html",
        active_page="online",
        theme=session.get("theme", "light"),
        room=room_data,
        is_p1=is_p1,
        is_p2=is_p2,
        should_poll=should_poll,
        name=session.get("name")
    )

@app.route("/room/<code>/next", methods=["POST"])
def room_next(code):
    code = code.upper()
    if code in ROOMS:
        room_data = ROOMS[code]
        if not room_data["match_over"]:
            room_data["p1_choice"] = None
            room_data["p2_choice"] = None
            room_data["round_result"] = None
    return redirect(url_for("room", code=code))

@app.route("/room/<code>/reset", methods=["POST"])
def room_reset(code):
    code = code.upper()
    if code in ROOMS:
        room_data = ROOMS[code]
        room_data["p1_score"] = 0
        room_data["p2_score"] = 0
        room_data["draws"] = 0
        room_data["round"] = 0
        room_data["p1_choice"] = None
        room_data["p2_choice"] = None
        room_data["round_result"] = None
        room_data["match_over"] = False
        room_data["match_result"] = None
        room_data["match_saved"] = False
    return redirect(url_for("room", code=code))

@app.route("/reset")
def reset():
    name = session.get("name")
    p1_name = session.get("p1_name")
    p2_name = session.get("p2_name")
    theme = session.get("theme", "light")
    game_mode = session.get("game_mode", "computer")
    difficulty = session.get("difficulty", "easy")
    streak = session.get("streak", 0)
    player_id = session.get("player_id")

    session.clear()
    if name:
        session["name"] = name
        session["p1_name"] = p1_name or name
        session["p2_name"] = p2_name or "Player 2"
        session["theme"] = theme
        session["game_mode"] = game_mode
        session["difficulty"] = difficulty
        session["streak"] = streak
        session["player_id"] = player_id or uuid.uuid4().hex
        init_session()
    return redirect(url_for("game"))

if __name__ == "__main__":
    app.run(debug=True)
