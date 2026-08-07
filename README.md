# 🪨📄✂️ Rock Paper Scissors Game

A Rock Paper Scissors game built in Python — playable in the terminal or as a web app using Flask.

## 📌 About

This project started as a simple command-line Rock Paper Scissors game and has grown into a more complete app with input validation, multiple game modes, score tracking, and a web-based UI.

## 🚀 Features

- Play Rock, Paper, or Scissors against the computer
- Choose input mode: type words (`rock`, `paper`, `scissor`) or numbers (`0`, `1`, `2`)
- Choose match mode: **Best of 3** or **Best of 5**
- Live score tracking (wins / losses / draws) throughout the match
- Final match result summary (win, lose, or draw the overall match)
- Colored terminal output using `colorama` (green for win, red for loss, cyan for draw)
- Web-based version using Flask, with clickable buttons instead of typing

## 🛠️ Tech Stack

- Python 3
- Flask (for the web version)
- colorama (for colored terminal output)

## 📁 Project Structure

```
rps-project/
├── rps_terminal.py     # Core game logic + terminal version
├── app.py              # Flask web app (reuses logic from rps_terminal.py)
└── templates/
    └── index.html      # Web UI
```

## ▶️ How to Run

### Terminal version
```bash
git clone <your-repo-link>
cd <your-repo-folder>
python rps_terminal.py
```
Follow the prompts to choose your input mode (words/numbers) and match mode (Best of 3/5).

### Web version
1. Install Flask
   ```bash
   pip install flask
   ```
2. Run the app
   ```bash
   python app.py
   ```
3. Open your browser at `http://127.0.0.1:5000`

## 🎮 Example (Terminal)

```
Choose input mode:
1. Words (rock, paper, scissor)
2. Numbers (0, 1, 2)
Enter 1 or 2: 1

Choose mode:
1. Best of 3
2. Best of 5
Enter 1 or 2: 1

--- Round 1 ---
Type rock, paper, or scissor: paper
You : Paper
Computer : Rock
You Win!

--- Final Score ---
Wins   : 2
Losses : 1
Draws  : 0
You won the match! 🎉
```

## 🗺️ Roadmap / Upcoming Features

- [ ] Rock Paper Scissors Lizard Spock variant
- [ ] "Computer is choosing..." animation delay
- [ ] Unit tests using `pytest`
- [ ] Deploy the web version live (Render / PythonAnywhere)
- [ ] Player vs Player mode

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are always welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
