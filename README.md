# Wordle: Multi‑Player Turn‑Based Edition

> **Group 14 • Python • Pygame • 2025**

This project is a local party version of the classic *Wordle* game. Up to **6 players** take turns guessing the **same hidden five‑letter word**, compete for points, and enjoy a lively scoreboard—all wrapped in a colorful GUI built with **Pygame**.

---
## ✨ Features
|  | Description |
|---|---|
| **Turn‑based multiplayer** | Choose 1 – 6 players, enter their names, then take turns guess‑by‑guess. |
| **Dynamic scoring** | 3 pts for a green (correct position), 2 pts for a yellow (present letter). The scoreboard updates live. |
| **Keyboard color sync** | On‑screen QWERTY keyboard mirrors Wordle colors for each guess. |
| **Dark & Bright colors** | Greens, bright yellows, and custom grays enhance readability. |
| **Background themes** | Separate background images for the menu and the game board. |
| **Home / End buttons** | Jump back to the main menu or end the match at any time. |

---
## 🖥️ How to Run
```bash
pip install pygame pyenchant
python main.py        # project entry‑point menu
python multiwordle.py # directly start the multi‑player mode
```
> **Note:**  If `pyenchant` complains about dictionaries, install system packages:<br>`sudo apt install libenchant-2-2` (Ubuntu) or brew equivalent.

---
## 📂 Project Structure
```
├── main.py            # start‑menu: choose single / multi mode
├── singlewordle.py    # 1‑player Wordle (classic)
├── multiwordle.py     # 1‑6 players turn‑based edition
├── word.py            # five‑letter word list
├── image/
│   ├── menu_bg.jpg    # background for menus
│   └── game_bg.jpg    # background for gameplay
└── README.md
```

---
## 🎮 Game Flow
1. **Select player count** (1–6) on the menu.
2. **Enter player names** – highlighted row shows whose name you are typing.
3. **Guess turns** – each player types a 5‑letter word ⏎.
4. **Color feedback** follows Wordle rules:
   * 🟩 Green = correct position
   * 🟨 Yellow = in word, wrong spot
   * ⬜ Gray = not in word
5. **Scoreboard** updates instantly. First to solve scores a bonus!
6. Press **Home** to restart or **End Game** to see the final ranking.

---
## ⚙️ Customisation
* **Word list**: replace or extend `word.py`.
* **Backgrounds**: drop new images in `image/`, update the filenames in code.
* **Colors / fonts**: tweak constants at the top of each `.py` file.

---
## 👥 Credits
*Developed by Group 14, National XYZ University, Software Engineering (Spring 2025).*