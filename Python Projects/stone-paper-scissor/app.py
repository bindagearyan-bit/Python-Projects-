print("THIS IS THE NEW VERSION - TEST 123")

from flask import Flask, render_template, request, session
import random
from rps_terminal import check

app = Flask(__name__)
app.secret_key = "rps_secret_key"

@app.route("/", methods=["GET", "POST"])
def home():
    if "started" not in session:
        session["started"] = False
        session["wins"] = 0
        session["losses"] = 0
        session["draws"] = 0
        session["round"] = 0
        session["total_rounds"] = 3

    result = None
    user_choice = None
    comp_choice = None
    match_over = False
    match_result = None

    if request.method == "POST":
        if "mode" in request.form:
            session["total_rounds"] = int(request.form["mode"])
            session["wins"] = 0
            session["losses"] = 0
            session["draws"] = 0
            session["round"] = 0
            session["started"] = True

        elif "choice" in request.form:
            choices = ["rock", "paper", "scissor"]
            user_choice = request.form["choice"]
            comp_choice = random.choice(choices)
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
        result=result,
        user_choice=user_choice,
        comp_choice=comp_choice,
        wins=session["wins"],
        losses=session["losses"],
        draws=session["draws"],
        round=session["round"],
        total_rounds=session["total_rounds"],
        match_over=match_over,
        match_result=match_result,
        started=session["started"]
    )

@app.route("/reset")
def reset():
    session.clear()
    return home()

if __name__ == "__main__":
    app.run(debug=True)
