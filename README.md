# 🪨📄✂️ Rock Paper Scissor — Match Ticket Arena

A full-featured Rock Paper Scissors web app built with Python + Flask, styled as a vintage "Match Ticket" — now live and packaged as an installable Android APK.

**Live app:** https://python-projects-p41c.onrender.com

_Last updated: August 2026_

## 📌 About

What started as a simple terminal script has grown into a complete web application with login, multiple game modes, a smart AI opponent, online multiplayer, a leaderboard, and a custom vintage ticket-stub visual theme — deployed live and shareable as an Android app.

## 🚀 Features

- **Login** — simple name entry to personalize the session
- **Vs Computer mode** with two difficulty levels:
  - Easy — random moves
  - Hard — tracks your move history and counters your most common choice
- **Local 2-Player mode** — two players share one device, taking turns
- **Online Multiplayer** — create or join a 5-character room code and play against a friend on a separate device, anywhere
- **Best of 3 / Best of 5** match length selection
- **Win streak tracker** — 🔥 badge shown after 2+ consecutive wins (vs Computer)
- **Match Leaderboard** — last 10 matches saved and displayed (player, opponent, result, mode, date)
- **Dark mode / Light mode** toggle, fully re-themed (not just background)
- **Rules and About pages**, all styled consistently
- Custom **Match Ticket** visual theme: parchment ticket card, punch-hole cutouts, Bebas Neue headings, Space Mono scoreboard text, crimson red accents
- Packaged as an **installable Android APK** via PWA Builder — shareable directly with friends, no Play Store needed

## 🛠️ Tech Stack

- Python 3
- Flask
- Jinja2 templates
- JSON file storage (leaderboard, no database needed)
- Deployed on Render
- Packaged with PWABuilder (PWA → APK)

## 📁 Project Structure

```
stone-paper-scissor/
├── app.py                  # Main Flask app — all routes and game logic
├── rps_terminal.py         # Original terminal version
├── requirements.txt        # Python dependencies (flask, gunicorn, colorama)
├── leaderboard.json        # Stored match history
├── static/
│   ├── manifest.json       # PWA manifest (for APK packaging)
│   ├── icon-192.png
│   └── icon-512.png
└── templates/
    ├── base.html            # Shared layout (nav, head, manifest link)
    ├── login.html
    ├── index.html           # Main game screen
    ├── rules.html
    ├── about.html
    ├── leaderboard.html
    ├── online.html          # Create/Join online room
    └── room.html            # Live online match screen
```

## ▶️ How to Run Locally

```bash
git clone <your-repo-link>
cd stone-paper-scissor
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

## 🌐 Play Online

Visit the live deployed version:
**https://python-projects-p41c.onrender.com**

## 📱 Install as an App (Android)

An APK is available for direct install — no Play Store required:
1. Download `RPS Arena.apk`
2. On your Android phone, tap the file
3. Allow "install from unknown sources" if prompted
4. Open "RPS Arena" from your home screen

## 🗺️ Roadmap / Ideas for Later

- [ ] Service worker for offline support
- [ ] App screenshots for a future Play Store listing
- [ ] Rock Paper Scissors Lizard Spock variant
- [ ] Unit tests using `pytest`

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are always welcome!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
