import pygame as p
import random
from chessengine import GameState, Move

# ----------------------------- CONSTANTS ----------------------------------
DIMENSION = 8
FPS = 60
HIGHLIGHT_COLOR = (246, 246, 105, 120)
CAPTURE_COLOR = (255, 0, 0, 120)
SPECIAL_COLOR = (0, 0, 255, 120)
SIDEBAR_COLOR = (50, 50, 50)
BUTTON_RADIUS = 15
WIDTH, HEIGHT = 900, 600  # Extra width for sidebar
BOARD_SIZE = HEIGHT
SQUARE_SIZE = BOARD_SIZE // DIMENSION
BOARD_RECT = p.Rect(0, 0, BOARD_SIZE, BOARD_SIZE)
SIDEBAR_RECT = p.Rect(BOARD_SIZE, 0, WIDTH-BOARD_SIZE, HEIGHT)

# ----------------------------- GLOBALS ------------------------------------
IMAGES = {}

def load_images():
    pieces = ['wP','wR','wN','wB','wQ','wK','bP','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))

class Button:
    def __init__(self, rect, color, text="", callback=None):
        self.rect = p.Rect(rect)
        self.color = color
        self.text = text
        self.callback = callback
        self.font = p.font.SysFont("comicsans", 20)
        self.hovered = False

    def draw(self, surface):
        c = tuple(min(255,int(x*1.2)) if self.hovered else x for x in self.color)
        p.draw.rect(surface, c, self.rect, border_radius=BUTTON_RADIUS)
        if self.text != "":
            txt = self.font.render(self.text, True, (0,0,0))
            surface.blit(txt, (self.rect.x + 5, self.rect.y + 5))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.callback:
            self.callback()

class GameUI:
    def __init__(self, gs):
        self.selected_sq = ()
        self.move_highlight = []
        self.undo_stack = []
        self.redo_stack = []
        self.gs = gs
        self.valid_moves = gs.getValidMoves()
        self.sidebar_buttons = []
        self.create_buttons()

    def create_buttons(self):
        margin = 20
        width = SIDEBAR_RECT.width - 2*margin
        height = 50
        y = margin
        # Undo Button
        self.sidebar_buttons.append(Button((BOARD_SIZE+margin, y, width, height), (200,200,200), "Undo", self.undo))
        y += height + margin
        # Redo Button
        self.sidebar_buttons.append(Button((BOARD_SIZE+margin, y, width, height), (200,200,200), "Redo", self.redo))
        y += height + margin
        # Restart Button
        self.sidebar_buttons.append(Button((BOARD_SIZE+margin, y, width, height), (200,200,200), "Restart", self.restart))
        y += height + margin
        # Quit Button
        self.sidebar_buttons.append(Button((BOARD_SIZE+margin, y, width, height), (200,200,200), "Quit", self.quit_game))

    def restart(self):
        self.gs.__init__()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.selected_sq = ()
        self.move_highlight.clear()
        self.valid_moves = self.gs.getValidMoves()

    def quit_game(self):
        p.quit()
        exit()

    def undo(self):
        if self.undo_stack:
            move = self.undo_stack.pop()
            self.gs.undoMove()
            self.redo_stack.append(move)
            self.valid_moves = self.gs.getValidMoves()

    def redo(self):
        if self.redo_stack:
            move = self.redo_stack.pop()
            self.gs.makeMove(move)
            self.undo_stack.append(move)
            self.valid_moves = self.gs.getValidMoves()

    def select_square(self, row, col):
        piece = self.gs.board[row][col]
        # Deselect
        if self.selected_sq == (row, col):
            self.selected_sq = ()
            self.move_highlight.clear()
            return None
        # Select piece
        if piece != "--" and ((piece[0]=='w' and self.gs.whiteToMove) or (piece[0]=='b' and not self.gs.whiteToMove)):
            self.selected_sq = (row, col)
            self.move_highlight.clear()
            for move in self.valid_moves:
                if move.startRow == row and move.startCol == col:
                    self.move_highlight.append({
                        'row': move.endRow,
                        'col': move.endCol,
                        'capture': move.pieceCaptured != "--",
                        'special': False
                    })
            return None
        else:
            return (row, col)  # Target square

    def draw_sidebar(self, screen):
        p.draw.rect(screen, SIDEBAR_COLOR, SIDEBAR_RECT)
        for btn in self.sidebar_buttons:
            btn.draw(screen)

    def update_hover(self, pos):
        for btn in self.sidebar_buttons:
            btn.check_hover(pos)

    def click_buttons(self, pos):
        for btn in self.sidebar_buttons:
            btn.check_click(pos)

def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_game_state(screen, ui):
    draw_board(screen)
    # Highlights
    for highlight in ui.move_highlight:
        r, c = highlight['row'], highlight['col']
        color = HIGHLIGHT_COLOR
        if highlight['capture']:
            color = CAPTURE_COLOR
        elif highlight['special']:
            color = SPECIAL_COLOR
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE), p.SRCALPHA)
        s.fill(color)
        screen.blit(s, (c*SQUARE_SIZE, r*SQUARE_SIZE))
    # Selected square
    if ui.selected_sq:
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE), p.SRCALPHA)
        s.fill((180,180,50,120))
        screen.blit(s, (ui.selected_sq[1]*SQUARE_SIZE, ui.selected_sq[0]*SQUARE_SIZE))
    draw_pieces(screen, ui.gs.board)
    ui.draw_sidebar(screen)

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT), p.RESIZABLE)
    p.display.set_caption("Python Chess")
    clock = p.time.Clock()
    load_images()

    gs = GameState()
    ui = GameUI(gs)
    player_clicks = []

    running = True
    while running:
        mouse_pos = p.mouse.get_pos()
        ui.update_hover(mouse_pos)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if SIDEBAR_RECT.collidepoint(e.pos):
                    ui.click_buttons(e.pos)
                    continue
                # Click on board
                row, col = e.pos[1]//SQUARE_SIZE, e.pos[0]//SQUARE_SIZE
                target = ui.select_square(row, col)
                if target:
                    move = Move(ui.selected_sq, target, gs.board)
                    if move in ui.valid_moves:
                        gs.makeMove(move)
                        ui.undo_stack.append(move)
                        ui.redo_stack.clear()
                        ui.selected_sq = ()
                        ui.move_highlight.clear()
                        ui.valid_moves = gs.getValidMoves()

        draw_game_state(screen, ui)
        clock.tick(FPS)
        p.display.flip()

if __name__ == "__main__":
    main()
