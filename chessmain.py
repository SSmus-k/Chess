import sys, os, pygame, math
from PyQt5 import QtWidgets
from chessengine import ChessEngine

# --- Paths ---
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# ---------------- SETTINGS DIALOG ----------------
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setFixedSize(400,300)
        self.settings = settings or {}

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Sound
        self.sound_cb = QtWidgets.QCheckBox('Enable Sounds')
        self.sound_cb.setChecked(self.settings.get('sound', True))
        layout.addWidget(self.sound_cb)

        # Move Highlight
        self.highlight_cb = QtWidgets.QCheckBox('Highlight Moves')
        self.highlight_cb.setChecked(self.settings.get('highlight', True))
        layout.addWidget(self.highlight_cb)

        # Fullscreen
        self.fullscreen_cb = QtWidgets.QCheckBox('Fullscreen')
        self.fullscreen_cb.setChecked(self.settings.get('fullscreen', False))
        layout.addWidget(self.fullscreen_cb)

        # Theme selection
        layout.addWidget(QtWidgets.QLabel('Color Theme:'))
        self.theme_cb = QtWidgets.QComboBox()
        self.theme_cb.addItems(['Modern Light', 'Modern Dark', 'Classic', 'Dark', 'Cream', 'Calm', 'Stormy'])
        self.theme_cb.setCurrentIndex(self.settings.get('theme',0))
        layout.addWidget(self.theme_cb)

        # Buttons
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(btns)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        # Modern styling
        self.setStyleSheet("""
            QDialog { background-color: #2E3440; color: #D8DEE9; }
            QCheckBox { spacing: 10px; font-size: 16px; }
            QComboBox { font-size: 16px; padding: 4px; background-color: #3B4252; color: #ECEFF4; border-radius: 5px; }
            QPushButton { background-color: #88C0D0; color: #2E3440; padding: 6px 12px; border-radius: 5px; }
            QPushButton:hover { background-color: #81A1C1; }
        """)

    def get_settings(self):
        return {
            'sound': self.sound_cb.isChecked(),
            'highlight': self.highlight_cb.isChecked(),
            'fullscreen': self.fullscreen_cb.isChecked(),
            'theme': self.theme_cb.currentIndex()
        }

# ---------------- CHESS BOARD UI ----------------
class ChessBoardUI:
    def __init__(self, screen, images, font):
        self.screen = screen
        self.images = images
        self.font = font

    def draw_board(self, engine, settings, selected=None, valid_moves=[], notification=''):
        themes = [
            {'bg': (240,240,240), 'light': (232,235,239), 'dark': (125,135,150)},
            {'bg': (30,30,30), 'light': (80,80,80), 'dark': (50,50,50)},
            {'bg': (245,245,220), 'light': (255,255,240), 'dark': (205,133,63)},
            {'bg': (20,20,20), 'light': (60,60,60), 'dark': (30,30,30)},
            {'bg': (255,253,208), 'light': (255,255,240), 'dark': (210,180,140)},
            {'bg': (200,220,230), 'light': (220,240,250), 'dark': (100,120,140)},
            {'bg': (60,70,90), 'light': (120,130,150), 'dark': (40,50,70)},
        ]
        theme = themes[settings.get('theme',0)]
        self.screen.fill(theme['bg'])

        # Check detection for highlighting king
        king_in_check = None
        for color, is_white in [('w', True), ('b', False)]:
            if engine.is_check(is_white):
                for r in range(8):
                    for c in range(8):
                        piece = engine.board[r][c]
                        if piece and piece[0]=='K' and piece[1]==color:
                            king_in_check = (r,c)

        # Draw squares and pieces
        for r in range(8):
            for c in range(8):
                base_color = theme['dark'] if (r+c)%2==0 else theme['light']
                rect = pygame.Rect(c*100, r*100, 100, 100)
                pygame.draw.rect(self.screen, base_color, rect, border_radius=8)
                if king_in_check == (r,c):
                    pygame.draw.rect(self.screen, (255,0,0), rect, 4, border_radius=8)

                piece = engine.board[r][c]
                if piece:
                    img = self.images.get(f'{piece[1]}{piece[0]}')
                    if img:
                        rect_img = img.get_rect(center=(c*100+50, r*100+50))
                        self.screen.blit(img, rect_img)

        # Highlight valid moves
        if settings['highlight'] and selected:
            for move in valid_moves:
                highlight_color = (255, 247, 200, 120)
                if move.is_castle or move.is_en_passant or move.promotion:
                    highlight_color = (220, 240, 255, 120)
                rect = pygame.Rect(move.end[1]*100, move.end[0]*100, 100, 100)
                surf = pygame.Surface((100,100), pygame.SRCALPHA)
                surf.fill(highlight_color)
                self.screen.blit(surf, rect.topleft)

        # Notifications
        if notification:
            notif = self.font.render(notification, True, (255,0,0))
            self.screen.blit(notif, (10, 760))

# ---------------- NAVBAR UI ----------------
class NavbarUI:
    def __init__(self, surface, options, font=None):
        self.surface = surface
        self.options = options
        self.font = font or pygame.font.SysFont('Arial', 22, bold=True)
        self.rects = []

    def draw(self):
        self.rects = []
        x = 0
        y = 810
        for opt in self.options:
            rect = pygame.Rect(x,y,140,40)
            pygame.draw.rect(self.surface, (57,62,70), rect, border_radius=8)
            pygame.draw.rect(self.surface, (255,211,105), rect, 2, border_radius=8)
            label = self.font.render(opt, True, (255,255,255))
            self.surface.blit(label, label.get_rect(center=rect.center))
            self.rects.append(rect)
            x += 140

    def handle_click(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                return self.options[i]
        return None

# ---------------- CHESS GAME ----------------
class ChessGame:
    def __init__(self, screen, settings, ai_color='b'):
        pygame.init()
        pygame.mixer.init()
        self.screen = screen
        self.settings = settings
        self.engine = ChessEngine()
        self.ai_color = ai_color
        self.selected = None
        self.valid_moves = []
        self.notification = ''
        self.images = self.load_assets()
        self.sounds = self.load_sounds()
        self.font = pygame.font.SysFont('Arial', 24)
        self.board_ui = ChessBoardUI(screen, self.images, self.font)
        self.navbar_ui = NavbarUI(screen, ['Menu','Undo','Settings','Exit'])
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = self.settings.get('fullscreen', False)
        if self.fullscreen:
            pygame.display.set_mode((800,850), pygame.FULLSCREEN)
        self.play_music()
        self._ai_wait = None

    # --- Assets ---
    def load_assets(self):
        images = {}
        for color in ['w','b']:
            for piece in ['K','Q','R','B','N','P']:
                path = os.path.join(IMAGES_DIR, f'{color}{piece}.png')
                if os.path.exists(path):
                    images[f'{color}{piece}'] = pygame.image.load(path)
                else:
                    img = pygame.Surface((80,80))
                    img.fill((200,200,200) if color=='w' else (50,50,50))
                    images[f'{color}{piece}'] = img
        return images

    # --- Sounds ---
    def load_sounds(self):
        sounds = {}
        for name in ['move','capture','check','checkmate','invalid']:
            path = os.path.join(SOUNDS_DIR, f'{name}.wav')
            if os.path.exists(path):
                try: sounds[name] = pygame.mixer.Sound(path)
                except: sounds[name]=None
            else: sounds[name]=None
        return sounds

    def play_sound(self, name):
        if self.settings.get('sound', True) and self.sounds.get(name):
            try: self.sounds[name].play()
            except: pass

    def play_music(self):
        path = os.path.join(SOUNDS_DIR, 'bg_music.mp3')
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except: pass

    # --- Game Loop ---
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.board_ui.draw_board(self.engine, self.settings, self.selected, self.valid_moves, self.notification)
            self.navbar_ui.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running=False
            elif event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: self.running=False
                if event.key==pygame.K_f: self.toggle_fullscreen()
                if event.key==pygame.K_u:
                    self.engine.undo_move()
                    self.play_sound('move')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                nav_action = self.navbar_ui.handle_click(event.pos)
                if nav_action=='Exit': self.running=False; return
                if nav_action=='Undo': self.engine.undo_move(); self.play_sound('move'); return
                if nav_action=='Settings': self.show_settings(); return
                if nav_action=='Menu': self.running=False; return
                self.handle_click(event.pos)

    def handle_click(self, pos):
        x,y = pos
        if not (0<=x<800 and 0<=y<800): return
        row, col = y//100, x//100
        if self.selected:
            piece_moves = [m for m in self.engine.get_valid_moves() if m.start==self.selected]
            for move in piece_moves:
                if move.end==(row,col):
                    self.engine.make_move(move)
                    self.play_sound('move')
                    self.selected=None
                    self.valid_moves=[]
                    return
            self.selected=None
            self.valid_moves=[]
        else:
            piece = self.engine.board[row][col]
            if piece and ((piece[1]=='w' and self.engine.white_to_move) or (piece[1]=='b' and not self.engine.white_to_move)):
                self.selected=(row,col)
                self.valid_moves=[m for m in self.engine.get_valid_moves() if m.start==(row,col)]

    def update(self):
        # AI logic
        import random
        if self.ai_color and ((self.engine.white_to_move and self.ai_color=='w') or (not self.engine.white_to_move and self.ai_color=='b')):
            if not self._ai_wait:
                self._ai_wait=pygame.time.get_ticks()+random.randint(500,1500)
            if pygame.time.get_ticks()>=self._ai_wait:
                move=self.engine.get_ai_move(2)
                if move: self.engine.make_move(move); self.play_sound('move')
                self._ai_wait=None

    # --- Settings / Fullscreen ---
    def show_settings(self):
        import sip
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        
        # Get the HWND or XID of the pygame window
        try:
            import pygame._sdl2.video as sdl2_video
            hwnd = sdl2_video.get_window_handle()
            # Wrap it as a QWidget for PyQt parent
            parent = sip.wrapinstance(int(hwnd), QtWidgets.QWidget)
        except:
            parent = None
        
        dlg = SettingsDialog(parent, settings=self.settings)
        if dlg.exec_():
            self.settings = dlg.get_settings()
            # Apply theme & fullscreen changes
            if self.settings['fullscreen'] != self.fullscreen:
                self.toggle_fullscreen()


    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((800,850), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((800,850), pygame.RESIZABLE)

# ---------------- LANDING SCREEN ----------------
class LandingScreen:
    def __init__(self, surface, chess_game):
        self.surface = surface
        self.chess_game = chess_game
        # Fonts
        self.title_font = pygame.font.SysFont('Calibri', 60, bold=True)
        self.btn_font = pygame.font.SysFont('Segoe UI', 28, bold=True)
        # Buttons
        self.buttons = [
            {'label':'Single Player','rect':pygame.Rect(250,250,300,70)},
            {'label':'Multiplayer','rect':pygame.Rect(250,340,300,70)},
            {'label':'Settings','rect':pygame.Rect(250,430,300,70)},
            {'label':'Music','rect':pygame.Rect(250,520,300,70)}
        ]
        self.hovered = [False]*len(self.buttons)
        # Colors
        self.bg_color = (28,34,44)
        self.btn_color = (50,60,80)
        self.btn_hover_color = (72,133,224)
        self.btn_border_color = (255,211,105)
        self.text_color = (255,255,255)

    def draw(self):
        self.surface.fill(self.bg_color)
        # Title
        title_surf = self.title_font.render("Project Code : Chess", True, (255,211,105))
        title_rect = title_surf.get_rect(center=(400, 150))
        self.surface.blit(title_surf, title_rect)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        for i, btn in enumerate(self.buttons):
            rect = btn['rect']
            self.hovered[i] = rect.collidepoint(mouse_pos)
            color = self.btn_hover_color if self.hovered[i] else self.btn_color
            pygame.draw.rect(self.surface, color, rect, border_radius=20)
            pygame.draw.rect(self.surface, self.btn_border_color, rect, 3, border_radius=20)
            label_surf = self.btn_font.render(btn['label'], True, self.text_color)
            self.surface.blit(label_surf, label_surf.get_rect(center=rect.center))

        pygame.display.flip()

    def get_clicked(self, pos):
        for i, btn in enumerate(self.buttons):
            if btn['rect'].collidepoint(pos):
                # Music toggle
                if btn['label'] == 'Music':
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    else:
                        self.chess_game.play_music()
                return btn['label']
        return None

# ---------------- MAIN ----------------
def main():
    pygame.init()
    screen=pygame.display.set_mode((800,850),pygame.RESIZABLE)
    pygame.display.set_caption('Python Chess')
    settings={'sound':True,'highlight':True,'fullscreen':False,'theme':0}
    running=True
    while running:
        game=ChessGame(screen,settings)
        landing=LandingScreen(screen,game)
        mode=None
        while running and not mode:
            for event in pygame.event.get():
                if event.type==pygame.QUIT: running=False
                if event.type==pygame.MOUSEBUTTONDOWN:
                    clicked=landing.get_clicked(event.pos)
                    if clicked=='Single Player': mode='single'
                    if clicked=='Multiplayer': mode='multi'
                    if clicked=='Settings': game.show_settings()
            landing.draw()

        while running and mode:
            game.ai_color='b' if mode=='single' else None
            game.run()
            mode=None

if __name__=='__main__':
    main()
