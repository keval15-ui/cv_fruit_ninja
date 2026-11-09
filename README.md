# Computer-Vision Fruit Ninja

A Fruit Ninja-style game controlled by index-finger tracking through a webcam.

## Project structure

```text
cv_fruit_ninja/
├── assets/
│   ├── images/
│   └── sounds/
├── src/
│   ├── __init__.py
│   ├── hand_tracker.py
│   ├── fruit.py
│   ├── blade.py
│   └── game_manager.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup

Use Python 3.10 or newer:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Add the required fruit, bomb, background, and sound assets to the
`assets/images` and `assets/sounds` directories.
