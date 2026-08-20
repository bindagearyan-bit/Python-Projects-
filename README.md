# 🪨📄✂️ Rock Paper Scissors Game

A Rock Paper Scissors game built in Python — playable in the terminal or as a full-featured web app using Flask.

_Last updated: August 2026_

## 📌 About

This project started as a simple command-line Rock Paper Scissors game and has grown into a complete web app with login, game modes, difficulty levels, dark/light theme, and animations.

## 🚀 Features

- Play Rock, Paper, or Scissors against the computer
- Choose input mode (terminal version): words (`rock`, `paper`, `scissor`) or numbers (`0`, `1`, `2`)
- Choose match mode: **Best of 3** or **Best of 5**
- Live score tracking (wins / losses / draws) throughout the match
- Final match result summary (win, lose, or draw the overall match)
- Colored terminal output using `colorama` (green for win, red for loss, cyan for draw)
- Web-based version using Flask, with clickable buttons instead of typing
- Simple login screen (enter your name to start playing)
- **2 Player mode** — play against a friend on the same device, with both player names shown
- **Difficulty mode** (vs Computer): Easy (random) or Hard (computer tracks your most common move and counters it)
- **Dark mode / Light mode** toggle
- Menu bar to switch game mode and difficulty mid-session
- Animated UI: fade-ins, button pop effects, and a "battle" emoji clash animation on each round

## 🛠️ Tech Stack

- Python 3
- Flask (for the web version)
- colorama (for colored terminal output)

## 📁 Project Structure

```
rps-project/
├── rps_terminal.py     # Core game logic + terminal version
├── app.py              # Flask web app (reuses logic from rps_terminal.py)
├── requirements.txt    # Python dependencies
├── .gitignore
└── templates/
    ├── login.html      # Name entry screen
    └── index.html      # Main game UI
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
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app
   ```bash
   python app.py
   ```
3. Open your browser at `http://127.0.0.1:5000`
4. Enter your name, pick a game mode (Vs Computer / 2 Player) and difficulty from the menu, then play

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
- [ ] Package as an installable APK to share with friends

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are always welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
