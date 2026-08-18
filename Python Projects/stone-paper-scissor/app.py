from flask import Flask, render_template, request, session
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

@app.route("/", methods=["GET", "POST"])
def home():
    if "name" not in session:
        if request.method == "POST" and "name" in request.form:
            session["name"] = request.form["name"]
            session["theme"] = "light"
        return render_template("login.html")

    if "started" not in session:
        session["started"] = False
        session["wins"] = 0
        session["losses"] = 0
        session["draws"] = 0
        session["round"] = 0
        session["total_rounds"] = 3
        session["game_mode"] = "computer"
        session["difficulty"] = "easy"
        session["history"] = []
        session["p1_choice"] = None

    result = None
    user_choice = None
    comp_choice = None
    match_over = False
    match_result = None
    waiting_p2 = False

    if request.method == "POST":
        if "mode" in request.form:
            session["total_rounds"] = int(request.form["mode"])
            session["wins"] = 0
            session["losses"] = 0
            session["draws"] = 0
            session["round"] = 0
            session["history"] = []
            session["started"] = True

        elif "game_mode" in request.form:
            session["game_mode"] = request.form["game_mode"]

        elif "difficulty" in request.form:
            session["difficulty"] = request.form["difficulty"]

        elif "theme" in request.form:
            session["theme"] = request.form["theme"]

        elif "choice" in request.form:
            user_choice = request.form["choice"]

            if session["game_mode"] == "2player":
                if session["p1_choice"] is None:
                    session["p1_choice"] = user_choice
                    waiting_p2 = True
                else:
                    p1 = session["p1_choice"]
                    p2 = user_choice
                    score = check(p1, p2)
                    user_choice = f"P1: {p1.capitalize()}"
                    comp_choice = f"P2: {p2.capitalize()}"
                    session["p1_choice"] = None

                    if score == 0:
                        result = "It's a draw!"
                        session["draws"] += 1
                    elif score == 1:
                        result = "Player 1 Wins!"
                        session["wins"] += 1
                    else:
                        result = "Player 2 Wins!"
                        session["losses"] += 1

                    session["round"] += 1
            else:
                choices = ["rock", "paper", "scissor"]
                if session["difficulty"] == "hard":
                    comp_choice = get_smart_computer_choice(session["history"])
                else:
                    comp_choice = random.choice(choices)

                session["history"].append(user_choice)
                score = check(comp_choice, user_choice)

                if score == 0:
                    result = "It's a draw!"
                    session["draws"] += 1
                elif score == 1:
                    result = "You Win!"
                    session["wins"] += 1
                else:
                    result = "You Lose!"
                    session["losses"] += 1

                session["round"] += 1

            if session["round"] >= session["total_rounds"]:
                match_over = True
                if session["wins"] > session["losses"]:
                    match_result = "You won the match! 🎉"
                elif session["losses"] > session["wins"]:
                    match_result = "You lost the match!"
                else:
                    match_result = "The match is a draw!"

    return render_template(
        "index.html",
        name=session.get("name"),
        theme=session.get("theme", "light"),
        game_mode=session.get("game_mode", "computer"),
        difficulty=session.get("difficulty", "easy"),
        result=result, user_choice=user_choice, comp_choice=comp_choice,
        wins=session["wins"], losses=session["losses"], draws=session["draws"],
        round=session["round"], total_rounds=session["total_rounds"],
        match_over=match_over, match_result=match_result,
        started=session["started"], waiting_p2=waiting_p2
    )

@app.route("/reset")
def reset():
    session.clear()
    return home()

if __name__ == "__main__":
    app.run(debug=True)
