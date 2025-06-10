# 🧠 Wumpus World logical Agent Game 

This project is a visual and interactive implementation of the **Wumpus World** AI problem, built using **Python (Tkinter GUI)** and **Prolog (via pyswip)**. It demonstrates how logical agents can reason under uncertainty to safely navigate a dangerous environment in search of gold.

---

## 🎮 Game Concept

- The world is a **4x4 grid**.
- You are an agent starting at cell `(1,1)`.
- Your mission: **Find the gold and return safely to the starting cell**.
- The world contains **dangerous pits** and a **Wumpus monster**.
- The game uses **percepts** such as:
  - **Breeze**: Pit nearby
  - **Stench**: Wumpus nearby
  - **Glitter**: Gold is in the current cell
  - **Scream**: Wumpus has been killed

---

## 🚀 Features

- 🧠 **Prolog-powered reasoning**: Logic-based movement, decision-making, and sensory updates
- 🎨 **Custom Tkinter GUI**: Beautiful and intuitive game board with modern styling
- 📜 **Game rules display**: Easy-to-read popup for first-time players
- 🧩 **Agent Actions**:
  - Move to adjacent cells
  - Shoot arrow (one shot)
  - Grab gold
  - Climb out of cave
- 📝 **Real-time action log**: Displays your move history
- 🎯 **Scoring System**:
  - Start with 30 points
  - Each move costs -1 point
  - Shooting arrow costs -10
  - Grabbing gold: +500
  - Game over if you fall in a pit or meet the Wumpus!

---

## ⚙️ Requirements

### 📦 Python Packages
Install the following with pip:

```bash
pip install pyswip pillow
