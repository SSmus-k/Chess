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
        # Board colors
        colors = [QColor(60,60,60), QColor(200,200,200)]
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                painter.fillRect(c*self.SQUARE_SIZE, r*self.SQUARE_SIZE,
                                 self.SQUARE_SIZE, self.SQUARE_SIZE,
                                 colors[(r+c)%2])
        # Highlights
        for sq in self.move_highlight:
            painter.fillRect(sq[1]*self.SQUARE_SIZE, sq[0]*self.SQUARE_SIZE,
                             self.SQUARE_SIZE, self.SQUARE_SIZE,
                             QColor(246,246,105,150))
        # Selected square
        if self.selected_sq:
            painter.fillRect(self.selected_sq[1]*self.SQUARE_SIZE, self.selected_sq[0]*self.SQUARE_SIZE,
                             self.SQUARE_SIZE, self.SQUARE_SIZE,
                             QColor(180,180,50,150))
        # Pieces
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = self.gs.board[r][c]
                if piece != "--":
                    painter.drawPixmap(c*self.SQUARE_SIZE, r*self.SQUARE_SIZE,
                                       self.piece_images[piece])

    def mousePressEvent(self, event):
        row = int(event.position().y()) // self.SQUARE_SIZE
        col = int(event.position().x()) // self.SQUARE_SIZE
        piece = self.gs.board[row][col]

        if self.selected_sq:
            target = (row, col)
            move = Move(self.selected_sq, target, self.gs.board)
            if move in self.valid_moves:
                self.gs.makeMove(move)
                self.main_window.undo_stack.append(move)  # push to undo stack
                self.main_window.redo_stack.clear()       # clear redo stack
                self.selected_sq = None
                self.move_highlight.clear()
                self.valid_moves = self.gs.getValidMoves()
                self.main_window.play_move_sound(capture=move.pieceCaptured != "--")
                self.main_window.update_turn_message()

                # If single-player and AI turn
                if self.main_window.singleplayer and not self.gs.whiteToMove:
                    QTimer.singleShot(500, self.main_window.ai_move)
            else:
                self.main_window.show_alert("Invalid move!")
                self.selected_sq = None
                self.move_highlight.clear()
        else:
            if piece != "--" and ((piece[0]=='w' and self.gs.whiteToMove) or (piece[0]=='b' and not self.gs.whiteToMove)):
                self.selected_sq = (row, col)
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
        self.singleplayer = False
        self.undo_stack = []
        self.redo_stack = []
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
        pygame.mixer.init()
        if os.path.exists("sounds/bg_music.mp3"):
            pygame.mixer.music.load("sounds/bg_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
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

            # Single-player undo: also undo AI move
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

            # Single-player redo: also redo AI move
            if self.singleplayer and not self.gs.whiteToMove and self.redo_stack:
                ai_move = self.redo_stack.pop()
                self.gs.makeMove(ai_move)
                self.undo_stack.append(ai_move)

            self.board_widget.valid_moves = self.gs.getValidMoves()
            self.board_widget.selected_sq = None
            self.board_widget.move_highlight.clear()
            self.board_widget.update()
            self.update_turn_message()

    # ---------- Restart / Singleplayer ----------
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

    def enable_singleplayer(self):
        self.singleplayer = True
        self.restart_game()
        self.show_alert("Single Player Mode: You play White")

    # ---------- Simple AI ----------
    def ai_move(self):
        moves = self.gs.getValidMoves()
        if moves:
            move = random.choice(moves)
            self.gs.makeMove(move)
            self.undo_stack.append(move)
            self.play_move_sound(capture=move.pieceCaptured != "--")
            self.board_widget.valid_moves = self.gs.getValidMoves()
            self.board_widget.update()
            self.update_turn_message()


# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessUI()
    sys.exit(app.exec())
