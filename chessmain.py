def handle_click(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                return self.options[i]
        return None
"""
chessmain.py

Handles UI, graphics, input, and sound using pygame and PyQt5.

Features:
- Single-player (vs AI) and multiplayer
- Board rendering, animations, move highlighting
- Menus/settings with PyQt5
- Sound effects for moves, captures, check, checkmate, invalid
- Move history, chess clock, undo, notifications
- Theme and fullscreen options
- Loads assets from assets/images and assets/sounds

"""

import sys
import os
import pygame
from PyQt5 import QtWidgets, QtCore
from chessengine import ChessEngine

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# --- PyQt5 Settings Dialog ---
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.settings = settings or {}
        layout = QtWidgets.QVBoxLayout()
        self.sound_cb = QtWidgets.QCheckBox('Enable Sounds')
        self.sound_cb.setChecked(self.settings.get('sound', True))
        self.theme_cb = QtWidgets.QComboBox()
        self.theme_cb.addItems(['Modern Light', 'Modern Dark', 'Classic', 'Dark', 'Cream', 'Calm', 'Stormy'])
        self.theme_cb.setCurrentIndex(self.settings.get('theme', 0))
        self.highlight_cb = QtWidgets.QCheckBox('Highlight Moves')
        self.highlight_cb.setChecked(self.settings.get('highlight', True))
        self.fullscreen_cb = QtWidgets.QCheckBox('Fullscreen')
        self.fullscreen_cb.setChecked(self.settings.get('fullscreen', False))
        layout.addWidget(self.sound_cb)
        layout.addWidget(QtWidgets.QLabel('Theme:'))
        layout.addWidget(self.theme_cb)
        layout.addWidget(self.highlight_cb)
        layout.addWidget(self.fullscreen_cb)
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(btns)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    def get_settings(self):
        return {
            'sound': self.sound_cb.isChecked(),
            'theme': self.theme_cb.currentIndex(),
            'highlight': self.highlight_cb.isChecked(),
            'fullscreen': self.fullscreen_cb.isChecked()
        }

# --- Main Chess Game ---
class ChessGame:
    def animate_move(self, move):
            # Simple animation: slide piece from start to end
            sr, sc = move.start
            er, ec = move.end
            img = self.images.get(f'{move.piece[1]}{move.piece[0]}')
            if not img:
                return
            frames = 10
            for i in range(1, frames+1):
                self.draw()
                x = sc*100 + (ec-sc)*100*i//frames + 50
                y = sr*100 + (er-sr)*100*i//frames + 50
                rect = img.get_rect(center=(x, y))
                self.screen.blit(img, rect)
                pygame.display.flip()
                pygame.time.delay(15)
    def __init__(self):
        pygame.init()
        self.settings = {'sound': True, 'theme': 0, 'highlight': True, 'fullscreen': False}
        self.screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
        pygame.display.set_caption('Python Chess')
        self.clock = pygame.time.Clock()
        self.engine = ChessEngine()
        self.selected = None
        self.valid_moves = []
        self.move_history = []
        self.running = True
        self.load_assets()
        self.sounds = self.load_sounds()
        self.font = pygame.font.SysFont('Arial', 24)
        self.ai_enabled = True
        self.ai_difficulty = 2
        self.move_highlight = True
        self.fullscreen = False
        self.turn = 'w'
        self.chess_clock = [900, 900]  # 15 min per player
        self.clock_running = [True, True]
        self.last_time = pygame.time.get_ticks()
        self.notification = ''
        self.music_playing = False
        self.play_music()
    def play_music(self):
        # Play background music if available
        music_path = os.path.join(SOUNDS_DIR, 'bg_music.mp3')
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception as e:
                print(f"Music error: {e}")

    def load_assets(self):
        self.images = {}
        for color in ['w', 'b']:
            for piece in ['K','Q','R','B','N','P']:
                path = os.path.join(IMAGES_DIR, f'{color}{piece}.png')
                if os.path.exists(path):
                    self.images[f'{color}{piece}'] = pygame.image.load(path)
                else:
                    self.images[f'{color}{piece}'] = pygame.Surface((80,80))
                    self.images[f'{color}{piece}'].fill((200,200,200) if color=='w' else (50,50,50))

    def load_sounds(self):
        sounds = {}
        for name in ['move','capture','check','checkmate','invalid']:
            path = os.path.join(SOUNDS_DIR, f'{name}.wav')
            if os.path.exists(path):
                sounds[name] = pygame.mixer.Sound(path)
            else:
                sounds[name] = None
        return sounds

    def play_sound(self, name):
        if self.settings['sound'] and self.sounds.get(name):
            self.sounds[name].play()

    def run(self, rotate_board=False):
        self.rotate_board = rotate_board
        self.navbar = Navbar(self.screen, ['Menu', 'Undo', 'Settings', 'Exit'])
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.navbar.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_u:
                    self.engine.undo_move()
                    self.play_sound('move')
                elif event.key == pygame.K_s:
                    self.show_settings()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check navbar first
                if self.navbar:
                    nav_action = self.navbar.handle_click(event.pos)
                    if nav_action == 'Exit':
                        self.running = False
                        return
                    elif nav_action == 'Undo':
                        self.engine.undo_move()
                        self.play_sound('move')
                        return
                    elif nav_action == 'Settings':
                        self.show_settings()
                        return
                    elif nav_action == 'Menu':
                        self.running = False
                        return
                self.handle_click(event.pos)

    def handle_click(self, pos):
        x, y = pos
        row, col = y // 100, x // 100
        if self.selected:
            # Only allow moves for the selected piece
            piece_moves = [m for m in self.engine.get_valid_moves() if m.start == self.selected]
            for move in piece_moves:
                if move.end == (row, col):
                    self.animate_move(move)
                    self.engine.make_move(move)
                    self.play_sound('move')
                    self.selected = None
                    self.valid_moves = []
                    return
            self.selected = None
            self.valid_moves = []
        else:
            piece = self.engine.board[row][col]
            if piece and ((piece[1] == 'w' and self.engine.white_to_move) or (piece[1] == 'b' and not self.engine.white_to_move)):
                self.selected = (row, col)
                # Only show moves for this piece
                self.valid_moves = [m for m in self.engine.get_valid_moves() if m.start == (row, col)]

    def update(self):
        # Check for checkmate
        if self.engine.is_checkmate(True):
            self.show_game_over('Black wins by checkmate!')
            self.running = False
        elif self.engine.is_checkmate(False):
            self.show_game_over('White wins by checkmate!')
            self.running = False
        # AI move with delay
        if self.ai_enabled and ((self.engine.white_to_move and self.turn=='w') or (not self.engine.white_to_move and self.turn=='b')):
            import random
            if not hasattr(self, '_ai_wait') or self._ai_wait is None:
                self._ai_wait = pygame.time.get_ticks() + random.randint(1000, 4000)
            if pygame.time.get_ticks() >= self._ai_wait:
                move = self.engine.get_ai_move(self.ai_difficulty)
                if move:
                    self.animate_move(move)
                    self.engine.make_move(move)
                    self.play_sound('move')
                self._ai_wait = None

    def draw(self):
        # Theme colors
        themes = [
            {'bg': (240,240,240), 'light': (232,235,239), 'dark': (125,135,150)}, # Modern Light
            {'bg': (30,30,30), 'light': (80,80,80), 'dark': (50,50,50)}, # Modern Dark
            {'bg': (245,245,220), 'light': (255,255,240), 'dark': (205,133,63)}, # Classic
            {'bg': (20,20,20), 'light': (60,60,60), 'dark': (30,30,30)}, # Dark
            {'bg': (255,253,208), 'light': (255,255,240), 'dark': (210,180,140)}, # Cream
            {'bg': (200,220,230), 'light': (220,240,250), 'dark': (100,120,140)}, # Calm
            {'bg': (60,70,90), 'light': (120,130,150), 'dark': (40,50,70)}, # Stormy
        ]
        theme = themes[self.settings.get('theme',0)]
        self.screen.fill(theme['bg'])
        # Find king in check
        king_in_check = None
        for color, is_white in [('w', True), ('b', False)]:
            if self.engine.is_check(is_white):
                # Find king position
                for r in range(8):
                    for c in range(8):
                        piece = self.engine.board[r][c]
                        if piece and piece[0] == 'K' and piece[1] == color:
                            king_in_check = (r, c)
        # Draw board
        for r in range(8):
            for c in range(8):
                color = theme['dark'] if (r+c)%2==0 else theme['light']
                rect = pygame.Rect(c*100, r*100, 100, 100)
                # Highlight king in check
                if king_in_check == (r, c):
                    pygame.draw.rect(self.screen, (255,0,0), rect)
                else:
                    pygame.draw.rect(self.screen, color, rect)
                piece = self.engine.board[r][c]
                if piece:
                    img = self.images.get(f'{piece[1]}{piece[0]}')
                    if img:
                        # Center the piece in the square
                        rect_img = img.get_rect(center=(c*100+50, r*100+50))
                        self.screen.blit(img, rect_img)
        for r in range(8):
            for c in range(8):
                draw_r, draw_c = r, c
                if getattr(self, 'rotate_board', False) and not self.engine.white_to_move:
                    draw_r, draw_c = 7 - r, 7 - c
                color = theme['dark'] if (draw_r+draw_c)%2==0 else theme['light']
                rect = pygame.Rect(draw_c*100, draw_r*100, 100, 100)
                # Highlight king in check
                if king_in_check == (r, c):
                    pygame.draw.rect(self.screen, (255,0,0), rect)
                else:
                    pygame.draw.rect(self.screen, color, rect)
                piece = self.engine.board[r][c]
                if piece:
                    img = self.images.get(f'{piece[1]}{piece[0]}')
                    if img:
                        # Center the piece in the square
                        rect_img = img.get_rect(center=(draw_c*100+50, draw_r*100+50))
                        self.screen.blit(img, rect_img)
        # Highlight
        if self.settings['highlight'] and self.selected:
            for move in self.valid_moves:
                highlight_color = (255, 247, 200)  # yellowish creamy
                if move.is_castle or move.is_en_passant or move.promotion:
                    highlight_color = (220, 240, 255)  # blueish white
                rect = pygame.Rect(move.end[1]*100, move.end[0]*100, 100, 100)
                pygame.draw.rect(self.screen, highlight_color, rect, border_radius=18)
        if self.settings['highlight'] and self.selected:
            for move in self.valid_moves:
                highlight_color = (255, 247, 200)  # yellowish creamy
                if move.is_castle or move.is_en_passant or move.promotion:
                    highlight_color = (220, 240, 255)  # blueish white
                end_r, end_c = move.end
                draw_r, draw_c = end_r, end_c
                if getattr(self, 'rotate_board', False) and not self.engine.white_to_move:
                    draw_r, draw_c = 7 - end_r, 7 - end_c
                rect = pygame.Rect(draw_c*100, draw_r*100, 100, 100)
                pygame.draw.rect(self.screen, highlight_color, rect, border_radius=18)
        # Notification
        if self.notification:
            notif = self.font.render(self.notification, True, (255,0,0))
            self.screen.blit(notif, (10, 760))
class Navbar:
    def __init__(self, surface, options):
        self.surface = surface
        self.options = options
        self.font = pygame.font.SysFont('Arial', 22, bold=True)
        self.rects = []
    def draw(self):
        self.rects = []
        x = 0
        for opt in self.options:
            rect = pygame.Rect(x, 0, 140, 40)
            pygame.draw.rect(self.surface, (57,62,70), rect)
            pygame.draw.rect(self.surface, (255,211,105), rect, 2)
            label = self.font.render(opt, True, (255,255,255))
            label_rect = label.get_rect(center=rect.center)
            self.surface.blit(label, label_rect)
            self.rects.append(rect)
            x += 140
    def handle_click(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                return self.options[i]
        return None
    def show_game_over(self, message):
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        QtWidgets.QMessageBox.information(None, 'Game Over', message)

    def animate_move(self, move):
        # Simple animation: slide piece from start to end
        sr, sc = move.start
        er, ec = move.end
        img = self.images.get(f'{move.piece[1]}{move.piece[0]}')
        if not img:
            return
        frames = 10
        for i in range(1, frames+1):
            self.draw()
            x = sc*100 + (ec-sc)*100*i//frames + 50
            y = sr*100 + (er-sr)*100*i//frames + 50
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
            pygame.display.flip()
            pygame.time.delay(15)

    def show_settings(self):
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        dlg = SettingsDialog(settings=self.settings)
        if dlg.exec_():
            self.settings = dlg.get_settings()
            if self.settings['fullscreen'] != self.fullscreen:
                self.toggle_fullscreen()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((800,800), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((800,800), pygame.RESIZABLE)

class LandingScreen:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont('Arial', 48, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 32)
        self.buttons = [
            {'label': 'Single Player', 'rect': pygame.Rect(250, 250, 300, 60)},
            {'label': 'Multiplayer', 'rect': pygame.Rect(250, 330, 300, 60)},
            {'label': 'Settings', 'rect': pygame.Rect(250, 410, 300, 60)},
            {'label': 'Color Options', 'rect': pygame.Rect(250, 490, 300, 60)},
            {'label': 'Music', 'rect': pygame.Rect(250, 570, 300, 60)}
        ]
        self.selected = None

    def draw(self):
        self.surface.fill((34, 40, 49))
        title = self.font.render('Python Chess', True, (255, 211, 105))
        self.surface.blit(title, (200, 120))
        for btn in self.buttons:
            pygame.draw.rect(self.surface, (57, 62, 70), btn['rect'], border_radius=18)
            pygame.draw.rect(self.surface, (255, 211, 105), btn['rect'], 3, border_radius=18)
            label = self.button_font.render(btn['label'], True, (255,255,255))
            label_rect = label.get_rect(center=btn['rect'].center)
            self.surface.blit(label, label_rect)
        pygame.display.flip()

    def get_clicked(self, pos):
        for i, btn in enumerate(self.buttons):
            if btn['rect'].collidepoint(pos):
                return btn['label']
        return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    pygame.display.set_caption('Python Chess')
    landing = LandingScreen(screen)
    running = True
    mode = None
    while running and not mode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = landing.get_clicked(event.pos)
                if clicked == 'Single Player':
                    mode = 'single'
                elif clicked == 'Multiplayer':
                    mode = 'multi'
                elif clicked == 'Settings':
                    # Placeholder: settings dialog
                    pass
                elif clicked == 'Color Options':
                    # Placeholder: color options
                    pass
                elif clicked == 'Music':
                    # Placeholder: music toggle
                    pass
        landing.draw()
    if mode == 'single':
        game = ChessGame()
        game.ai_enabled = True
        game.run()
    elif mode == 'multi':
        game = ChessGame()
        game.ai_enabled = False
        game.run()

if __name__ == '__main__':
    main()
