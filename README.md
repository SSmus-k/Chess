# Python Chess Game

## How to Add Assets

- Place chess piece images in `assets/images/`.
  - Name them as `wK.png`, `wQ.png`, `wR.png`, `wB.png`, `wN.png`, `wP.png` for white pieces, and `bK.png`, `bQ.png`, `bR.png`, `bB.png`, `bN.png`, `bP.png` for black pieces.
  - Board tile images can also be added for custom themes (optional).
- Place sound effects in `assets/sounds/`.
  - Use `move.wav`, `capture.wav`, `check.wav`, `checkmate.wav`, `invalid.wav` for respective events.

## Running the Game

1. Install dependencies:
   - `pip install pygame PyQt5`
2. Run the game:
   - `python chessmain.py`

## Features
- Single-player (vs AI) and multiplayer
- Modern/classic themes, dark/light modes
- Sound effects, move highlighting, animations
- Chess clock, move history, undo, notifications
- Settings menu (PyQt5)

## Notes
- All logic is in `chessengine.py`.
- All UI and input is in `chessmain.py`.
- All assets must be placed in the `assets/` folder as described above.
