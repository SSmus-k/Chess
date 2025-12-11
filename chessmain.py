import sys, os, random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout
)
from PyQt6.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer
import pygame

from chessengine import GameState, Move  # your existing engine

# ------------------- Chess Board Widget -------------------
class ChessBoardWidget(QWidget):
    DIMENSION = 8
    SQUARE_SIZE = 70

    def __init__(self, gs, main_window, parent=None):
        super().__init__(parent)
        self.gs = gs
        self.main_window = main_window
        self.selected_sq = None
        self.valid_moves = self.gs.getValidMoves()
        self.piece_images = {}
        self.move_highlight = []
        self.load_images()
        self.setFixedSize(self.DIMENSION*self.SQUARE_SIZE, self.DIMENSION*self.SQUARE_SIZE)

    def load_images(self):
        pieces = ['wP','wR','wN','wB','wQ','wK','bP','bR','bN','bB','bQ','bK']
        for piece in pieces:
            path = os.path.join("images", f"{piece}.png")
            if os.path.exists(path):
                self.piece_images[piece] = QPixmap(path).scaled(self.SQUARE_SIZE, self.SQUARE_SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        colors = [QColor(60,60,60), QColor(200,200,200)]
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                painter.fillRect(c*self.SQUARE_SIZE, r*self.SQUARE_SIZE,
                                 self.SQUARE_SIZE, self.SQUARE_SIZE,
                                 colors[(r+c)%2])
        # draw highlights (available moves)
        for sq in self.move_highlight:
            painter.fillRect(sq[1]*self.SQUARE_SIZE, sq[0]*self.SQUARE_SIZE,
                             self.SQUARE_SIZE, self.SQUARE_SIZE,
                             QColor(246,246,105,150))
        # draw selected square overlay
        if self.selected_sq:
            painter.fillRect(self.selected_sq[1]*self.SQUARE_SIZE, self.selected_sq[0]*self.SQUARE_SIZE,
                             self.SQUARE_SIZE, self.SQUARE_SIZE,
                             QColor(180,180,50,150))
        # draw pieces (only if image loaded)
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = self.gs.board[r][c]
                if piece != "--" and piece in self.piece_images:
                    painter.drawPixmap(c*self.SQUARE_SIZE, r*self.SQUARE_SIZE,
                                       self.piece_images[piece])

    def mousePressEvent(self, event):
        # get board coordinates
        row = int(event.position().y()) // self.SQUARE_SIZE
        col = int(event.position().x()) // self.SQUARE_SIZE

        # bounds check (safe)
        if row < 0 or row >= self.DIMENSION or col < 0 or col >= self.DIMENSION:
            return

        piece = self.gs.board[row][col]

        if self.selected_sq:
            target = (row, col)
            move = Move(self.selected_sq, target, self.gs.board)
            # check in current move list
            if move in self.valid_moves:
                # make the move
                self.gs.makeMove(move)
                self.main_window.undo_stack.append(move)
                self.main_window.redo_stack.clear()

                # clear selection & highlights
                self.selected_sq = None
                self.move_highlight.clear()

                # update local valid_moves from engine
                self.valid_moves = self.gs.getValidMoves()

                # play sound & update UI
                self.main_window.play_move_sound(capture=move.pieceCaptured != "--")
                self.main_window.update_turn_message()

                # if singleplayer is ON, detect if now it's AI's turn and schedule it
                if self.main_window.singleplayer:
                    ai_turn = (self.gs.whiteToMove and self.main_window.ai_plays_white) \
                            or (not self.gs.whiteToMove and not self.main_window.ai_plays_white)
                    if ai_turn:
                        # schedule AI a little later so GUI refreshes
                        QTimer.singleShot(200, self.main_window.ai_move)

            else:
                self.main_window.show_alert("Invalid move!")
                self.selected_sq = None
                self.move_highlight.clear()
        else:
            # select a piece if it belongs to current player
            if piece != "--" and ((piece[0]=='w' and self.gs.whiteToMove) or (piece[0]=='b' and not self.gs.whiteToMove)):
                self.selected_sq = (row, col)
                # build highlight list (endRow, endCol) for moves starting from this square
                self.move_highlight = [(m.endRow, m.endCol) for m in self.valid_moves if m.startRow==row and m.startCol==col]
            else:
                self.main_window.show_alert("Select a valid piece!")
        self.update()

# ------------------- Main UI -------------------
class ChessUI(QMainWindow):
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Chess")
        self.gs = GameState()

        # game / ai settings
        self.singleplayer = False
        self.ai_level = None            # 'Easy' / 'Medium' / 'Hard' / 'Grandmaster'
        self.ai_plays_white = False     # whether AI plays white (if False, AI plays black)
        self.ai_player_side = 'black'

        # undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # initialize audio and UI
        self.init_pygame_sounds()
        self.init_ui()
        self.show()

    # ---------- UI ----------
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        h_layout = QHBoxLayout()
        central_widget.setLayout(h_layout)

        # Chessboard
        self.board_widget = ChessBoardWidget(self.gs, main_window=self)
        h_layout.addWidget(self.board_widget)

        # Sidebar
        sidebar = QVBoxLayout()
        h_layout.addLayout(sidebar)

        self.message_label = QLabel("White's Turn")
        self.message_label.setFont(QFont("Arial", 14))
        self.message_label.setStyleSheet("color: white;")
        sidebar.addWidget(self.message_label)

        # Buttons
        self.add_button(sidebar, "Undo", self.undo_move)
        self.add_button(sidebar, "Redo", self.redo_move)
        self.add_button(sidebar, "Restart", self.restart_game)
        self.add_button(sidebar, "Single Player", self.enable_singleplayer)
        self.add_button(sidebar, "Quit", self.close)

        sidebar.addStretch()
        central_widget.setStyleSheet("background-color: #1e1e1e;")

    def add_button(self, layout, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
            }
        """)
        layout.addWidget(btn)

    # ---------- Sounds ----------
    def init_pygame_sounds(self):
        try:
            pygame.mixer.init()
        except Exception:
            pass
        if os.path.exists("sounds/bg_music.mp3"):
            try:
                pygame.mixer.music.load("sounds/bg_music.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except Exception:
                pass
        self.move_sound = pygame.mixer.Sound("sounds/move.wav") if os.path.exists("sounds/move.wav") else None
        self.capture_sound = pygame.mixer.Sound("sounds/capture.wav") if os.path.exists("sounds/capture.wav") else None

    def play_move_sound(self, capture=False):
        if capture and self.capture_sound:
            self.capture_sound.play()
        elif self.move_sound:
            self.move_sound.play()

    # ---------- Controls ----------
    def update_turn_message(self):
        if self.gs.whiteToMove:
            self.message_label.setText("White's Turn")
        else:
            self.message_label.setText("Black's Turn")

    def show_alert(self, msg):
        self.message_label.setText(msg)

    # ---------- Undo / Redo ----------
    def undo_move(self):
        if self.undo_stack:
            move = self.undo_stack.pop()
            self.gs.undoMove()
            self.redo_stack.append(move)

            # if playing vs AI, undo the AI's last move too (if available)
            if self.singleplayer and not self.gs.whiteToMove and self.undo_stack:
                ai_move = self.undo_stack.pop()
                self.gs.undoMove()
                self.redo_stack.append(ai_move)

            self.board_widget.valid_moves = self.gs.getValidMoves()
            self.board_widget.selected_sq = None
            self.board_widget.move_highlight.clear()
            self.board_widget.update()
            self.update_turn_message()

    def redo_move(self):
        if self.redo_stack:
            move = self.redo_stack.pop()
            self.gs.makeMove(move)
            self.undo_stack.append(move)

            # if singleplayer, redo AI's move too if available
            if self.singleplayer and not self.gs.whiteToMove and self.redo_stack:
                ai_move = self.redo_stack.pop()
                self.gs.makeMove(ai_move)
                self.undo_stack.append(ai_move)

            self.board_widget.valid_moves = self.gs.getValidMoves()
            self.board_widget.selected_sq = None
            self.board_widget.move_highlight.clear()
            self.board_widget.update()
            self.update_turn_message()

    # ---------- Restart ----------
    def restart_game(self):
        self.gs.__init__()
        self.board_widget.selected_sq = None
        self.board_widget.move_highlight.clear()
        self.board_widget.valid_moves = self.gs.getValidMoves()
        self.board_widget.update()
        self.update_turn_message()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.singleplayer = False
        self.ai_level = None

    # ---------- Singleplayer / Difficulty ----------
        # ---------- Singleplayer Mode ----------
    def enable_singleplayer(self):
        self.singleplayer = True
        self.show_alert("Single Player: Select AI Side")

        sidebar = self.centralWidget().layout().itemAt(1).layout()

        # Clear old difficulty buttons (if user presses again)
        for i in reversed(range(sidebar.count())):
            item = sidebar.itemAt(i)
            w = item.widget()
            if isinstance(w, QPushButton) and w.text() in ["AI = White", "AI = Black", "Easy", "Medium", "Hard", "Grandmaster"]:
                sidebar.removeWidget(w)
                w.deleteLater()

        # Side selection
        label = QLabel("AI plays as:")
        label.setStyleSheet("color:white;")
        sidebar.addWidget(label)

        btn_white = QPushButton("AI = White")
        btn_black = QPushButton("AI = Black")

        for b in (btn_white, btn_black):
            b.setStyleSheet("background-color:#555;color:white;border-radius:5px;padding:3px;")

        btn_white.clicked.connect(lambda: self.set_ai_side("white"))
        btn_black.clicked.connect(lambda: self.set_ai_side("black"))

        sidebar.addWidget(btn_white)
        sidebar.addWidget(btn_black)

    def set_ai_side(self, side):
        self.ai_plays_white = (side == "white")
        self.show_alert(f"AI will play as {side.capitalize()}. Select difficulty now.")

        sidebar = self.centralWidget().layout().itemAt(1).layout()

        difficulties = ["Easy", "Medium", "Hard", "Grandmaster"]
        for level in difficulties:
            btn = QPushButton(level)
            btn.setStyleSheet("background-color:#555;color:white;border-radius:5px;padding:3px;")
            btn.clicked.connect(lambda checked, l=level: self.set_ai_difficulty(l))
            sidebar.addWidget(btn)

    def set_ai_difficulty(self, level):
        self.ai_level = level
        self.show_alert(f"Difficulty: {level}. Game starting...")

        # Only restart after side + difficulty are set
        self.restart_game()

        # If AI plays white, make AI move immediately
        if self.singleplayer and self.ai_plays_white:
            QTimer.singleShot(500, self.ai_move)


    def set_ai_difficulty(self, level):
        self.ai_level = level
        self.show_alert(f"AI Difficulty set to {level}")
        # remove difficulty buttons after selection
        if hasattr(self, 'difficulty_buttons'):
            for btn in self.difficulty_buttons:
                btn.setParent(None)
            del self.difficulty_buttons

    # ---------- AI ----------
    def ai_move(self):
        # debug: uncomment to see calls in console
        # print("ai_move called; whiteToMove:", self.gs.whiteToMove, "ai_plays_white:", self.ai_plays_white)

        moves = self.gs.getValidMoves()
        if not moves:
            return

        # choose move by difficulty
        if self.ai_level == 'Easy':
            move = random.choice(moves)
        elif self.ai_level == 'Medium':
            move = self.minimax_move(depth=1)
        elif self.ai_level == 'Hard':
            move = self.minimax_move(depth=2)
        elif self.ai_level == 'Grandmaster':
            move = self.minimax_move(depth=3)
        else:
            move = random.choice(moves)

        # perform AI move and update UI
        self.gs.makeMove(move)
        self.undo_stack.append(move)
        self.play_move_sound(capture=move.pieceCaptured != "--")
        self.board_widget.valid_moves = self.gs.getValidMoves()
        self.board_widget.update()
        self.update_turn_message()

    # ---------- Minimax ----------
    def minimax_move(self, depth):
        moves = self.gs.getValidMoves()
        best_move = None
        if self.gs.whiteToMove:
            max_score = -float('inf')
            for move in moves:
                self.gs.makeMove(move)
                score = self.minimax(depth-1, False)
                self.gs.undoMove()
                if score > max_score:
                    max_score = score
                    best_move = move
        else:
            min_score = float('inf')
            for move in moves:
                self.gs.makeMove(move)
                score = self.minimax(depth-1, True)
                self.gs.undoMove()
                if score < min_score:
                    min_score = score
                    best_move = move
        return best_move

    def minimax(self, depth, is_maximizing):
        if depth == 0:
            return self.evaluate_board()
        moves = self.gs.getValidMoves()
        if is_maximizing:
            max_score = -float('inf')
            for move in moves:
                self.gs.makeMove(move)
                score = self.minimax(depth-1, False)
                self.gs.undoMove()
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            for move in moves:
                self.gs.makeMove(move)
                score = self.minimax(depth-1, True)
                self.gs.undoMove()
                min_score = min(min_score, score)
            return min_score

    def evaluate_board(self):
        piece_values = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K':0}
        score = 0
        for row in self.gs.board:
            for piece in row:
                if piece != "--":
                    value = piece_values[piece[1]]
                    if piece[0] == 'w':
                        score += value
                    else:
                        score -= value
        return score

# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessUI()
    sys.exit(app.exec())
