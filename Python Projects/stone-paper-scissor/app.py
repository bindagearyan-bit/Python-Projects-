from flask import Flask, render_template, request, session, redirect, url_for
import random
from rps_terminal import check
from collections import Counter

app = Flask(__name__)
app.secret_key = "rps_secret_key"

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

@app.route("/", methods=["GET", "POST"])
def home():
    if "name" not in session:
        if request.method == "POST" and "name" in request.form:
            name = request.form.get("name", "").strip()
            if name:
                session["name"] = name
                session["p1_name"] = name
                session["theme"] = "light"
                init_session()
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")

    init_session()

    result = None
    user_choice = None
    comp_choice = None
    match_over = False
    match_result = None
    waiting_p2 = False

    if request.method == "POST":
        if "update_names" in request.form:
            p1 = request.form.get("p1_name", "").strip()
            p2 = request.form.get("p2_name", "").strip()
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

                score = check(comp_choice, user_choice)

                if score == 0:
                    result = "It's a draw!"
                    session["draws"] = session.get("draws", 0) + 1
                elif score == 1:
                    result = "You Win!"
                    session["wins"] = session.get("wins", 0) + 1
                else:
                    result = "You Lose!"
                    session["losses"] = session.get("losses", 0) + 1

                session["round"] = session.get("round", 0) + 1

            if session.get("round", 0) >= session.get("total_rounds", 3):
                match_over = True
                wins = session.get("wins", 0)
                losses = session.get("losses", 0)
                if session.get("game_mode") == "2player":
                    if wins > losses:
                        match_result = f"{p1_name} won the match! 🎉"
                    elif losses > wins:
                        match_result = f"{p2_name} won the match! 🎉"
                    else:
                        match_result = "The match is a draw!"
                else:
                    if wins > losses:
                        match_result = "You won the match! 🎉"
                    elif losses > wins:
                        match_result = "You lost the match!"
                    else:
                        match_result = "The match is a draw!"

    return render_template(
        "index.html",
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
        waiting_p2=waiting_p2
    )

@app.route("/reset")
def reset():
    name = session.get("name")
    p1_name = session.get("p1_name")
    p2_name = session.get("p2_name")
    theme = session.get("theme", "light")
    game_mode = session.get("game_mode", "computer")
    session.clear()
    if name:
        session["name"] = name
        session["p1_name"] = p1_name or name
        session["p2_name"] = p2_name or "Player 2"
        session["theme"] = theme
        session["game_mode"] = game_mode
        init_session()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

