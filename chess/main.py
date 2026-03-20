'''
    Upgraded Chess Main — Enhanced Pygame UI
    ─────────────────────────────────────────
    Controls:
      Z         → Undo last move
      Y         → Redo last undone move
      R         → Reset board
      Click UI  → Undo / Redo / New Game buttons in panel
'''

import sys
import pygame as p
from engine import GameState, Move
from chessAi import findBestMove, findRandomMoves
from multiprocessing import Process, Queue

# ── Layout ────────────────────────────────────────────────────────────────────
BOARD_SIZE       = 560          # board is square
SQ_SIZE          = BOARD_SIZE // 8
PANEL_WIDTH      = 260
LABEL_SIZE       = 24           # rank/file label strip
WINDOW_W         = BOARD_SIZE + LABEL_SIZE + PANEL_WIDTH
WINDOW_H         = BOARD_SIZE + LABEL_SIZE + 60   # +60 for top status bar
BOARD_OFFSET_X   = LABEL_SIZE
BOARD_OFFSET_Y   = 60           # room for status bar at top
DIMENSION        = 8
MAX_FPS          = 60
IMAGES           = {}

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG            = (22, 21, 28)
C_PANEL_BG      = (30, 29, 38)
C_PANEL_BORDER  = (55, 53, 70)
C_LIGHT_SQ      = (237, 238, 209)
C_DARK_SQ       = (119, 153, 82)
C_HIGHLIGHT     = (100, 149, 237)      # selected piece
C_POSSIBLE      = (255, 220, 50)       # possible move dot
C_LAST_MOVE     = (205, 210, 106)      # last move flash
C_CHECK         = (220, 60, 60)        # king in check
C_STATUS_WHITE  = (240, 240, 240)
C_STATUS_BLACK  = (50, 50, 50)
C_ACCENT        = (100, 180, 100)
C_BTN_UNDO      = (70, 130, 180)
C_BTN_REDO      = (70, 160, 120)
C_BTN_NEW       = (180, 80, 80)
C_BTN_HOVER_ADD = 30
C_TEXT_LIGHT    = (230, 230, 230)
C_TEXT_DIM      = (160, 160, 160)
C_MOVE_EVEN     = (36, 35, 46)
C_MOVE_ODD      = (28, 27, 36)
C_MOVE_CURRENT  = (55, 80, 110)


# ── Fonts (initialised in main) ───────────────────────────────────────────────
FONT_TITLE   = None
FONT_STATUS  = None
FONT_LABEL   = None
FONT_MOVE    = None
FONT_BTN     = None
FONT_PANEL   = None


def init_fonts():
    global FONT_TITLE, FONT_STATUS, FONT_LABEL, FONT_MOVE, FONT_BTN, FONT_PANEL
    FONT_TITLE  = p.font.SysFont("Segoe UI", 26, bold=True)
    FONT_STATUS = p.font.SysFont("Segoe UI", 18, bold=True)
    FONT_LABEL  = p.font.SysFont("Segoe UI", 14)
    FONT_MOVE   = p.font.SysFont("Consolas",  13)
    FONT_BTN    = p.font.SysFont("Segoe UI", 15, bold=True)
    FONT_PANEL  = p.font.SysFont("Segoe UI", 15, bold=True)


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp',
              'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        img = p.image.load("images1/" + piece + ".png")
        IMAGES[piece] = p.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))


# ─────────────────────────────────────────────────────────────────────────────
# Helper: draw a rounded button, return True if hovered
# ─────────────────────────────────────────────────────────────────────────────
def draw_button(screen, rect, text, base_color, hover=False, radius=10):
    color = tuple(min(255, c + C_BTN_HOVER_ADD) for c in base_color) if hover else base_color
    shadow = p.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
    p.draw.rect(screen, (10, 10, 15), shadow, border_radius=radius)
    p.draw.rect(screen, color, rect, border_radius=radius)
    p.draw.rect(screen, (255, 255, 255, 60), rect, 1, border_radius=radius)
    txt = FONT_BTN.render(text, True, (255, 255, 255))
    screen.blit(txt, txt.get_rect(center=rect.center))


# ─────────────────────────────────────────────────────────────────────────────
# Menu screens
# ─────────────────────────────────────────────────────────────────────────────
def draw_menu_bg(screen):
    screen.fill(C_BG)
    # subtle diagonal gradient lines
    for i in range(0, WINDOW_W + WINDOW_H, 40):
        p.draw.line(screen, (30, 29, 40), (i, 0), (0, i), 1)


def menu_button(screen, rect, text, base_col, hover_col, mouse_pos, font=None):
    f = font or FONT_BTN
    hovered = rect.collidepoint(mouse_pos)
    col = hover_col if hovered else base_col
    shadow = p.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
    p.draw.rect(screen, (0, 0, 0), shadow, border_radius=16)
    p.draw.rect(screen, col, rect, border_radius=16)
    p.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=16)
    txt = f.render(text, True, (255, 255, 255))
    screen.blit(txt, txt.get_rect(center=rect.center))
    return hovered


def showModeSelect(screen):
    clock = p.time.Clock()
    btn_w, btn_h = 300, 60
    cx = WINDOW_W // 2
    btn1 = p.Rect(cx - btn_w // 2, 320, btn_w, btn_h)
    btn2 = p.Rect(cx - btn_w // 2, 410, btn_w, btn_h)

    title_font = p.font.SysFont("Segoe UI", 54, bold=True)
    sub_font   = p.font.SysFont("Segoe UI", 20)

    while True:
        draw_menu_bg(screen)
        mouse = p.mouse.get_pos()

        # Title
        t1 = title_font.render("♟  CHESS", True, (255, 255, 255))
        t2 = sub_font.render("Choose your game mode", True, (160, 160, 180))
        screen.blit(t1, t1.get_rect(centerx=cx, y=160))
        screen.blit(t2, t2.get_rect(centerx=cx, y=240))

        menu_button(screen, btn1, "Human  vs  AI",    (60, 130, 200), (90, 160, 240), mouse)
        menu_button(screen, btn2, "Human  vs  Human", (60, 160, 100), (90, 200, 130), mouse)

        p.display.flip()
        clock.tick(60)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if btn1.collidepoint(e.pos): return "AI"
                if btn2.collidepoint(e.pos): return "HUMAN"


def showColorSelect(screen):
    clock = p.time.Clock()
    btn_w, btn_h = 260, 60
    cx = WINDOW_W // 2
    btn1 = p.Rect(cx - btn_w // 2, 320, btn_w, btn_h)
    btn2 = p.Rect(cx - btn_w // 2, 410, btn_w, btn_h)
    title_font = p.font.SysFont("Segoe UI", 42, bold=True)

    while True:
        draw_menu_bg(screen)
        mouse = p.mouse.get_pos()
        t = title_font.render("Choose Your Side", True, (255, 255, 255))
        screen.blit(t, t.get_rect(centerx=cx, y=200))
        menu_button(screen, btn1, "▷  Play as White", (210, 205, 195), (240, 235, 225), mouse,
                    font=p.font.SysFont("Segoe UI", 18, bold=True))
        menu_button(screen, btn2, "▷  Play as Black", (45, 45, 55),   (75, 75, 90),   mouse,
                    font=p.font.SysFont("Segoe UI", 18, bold=True))
        p.display.flip()
        clock.tick(60)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if btn1.collidepoint(e.pos): return True,  False  # human=white, bot=black
                if btn2.collidepoint(e.pos): return False, True   # bot=white,   human=black


def showDifficultySelect(screen):
    clock = p.time.Clock()
    btn_w, btn_h = 260, 60
    cx = WINDOW_W // 2
    btns = [
        p.Rect(cx - btn_w // 2, 280, btn_w, btn_h),
        p.Rect(cx - btn_w // 2, 370, btn_w, btn_h),
        p.Rect(cx - btn_w // 2, 460, btn_w, btn_h),
    ]
    labels   = ["🟢  Easy",   "🟡  Medium",   "🔴  Hard"]
    colors   = [(60, 160, 80), (180, 140, 40), (180, 60, 60)]
    hovers   = [(90, 200, 110),(210, 170, 60), (220, 90, 90)]
    diffs    = ["EASY", "MEDIUM", "HARD"]
    title_font = p.font.SysFont("Segoe UI", 42, bold=True)
    desc_font  = p.font.SysFont("Segoe UI", 16)
    descs = ["Random moves — great for beginners",
             "Thinks 3 moves ahead",
             "Thinks 4 moves ahead with opening book"]

    while True:
        draw_menu_bg(screen)
        mouse = p.mouse.get_pos()
        t = title_font.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(t, t.get_rect(centerx=cx, y=160))

        for i, (btn, lbl, col, hov) in enumerate(zip(btns, labels, colors, hovers)):
            menu_button(screen, btn, lbl, col, hov, mouse)
            if btn.collidepoint(mouse):
                d = desc_font.render(descs[i], True, (180, 180, 200))
                screen.blit(d, d.get_rect(centerx=cx, y=btn.bottom + 6))

        p.display.flip()
        clock.tick(60)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for i, btn in enumerate(btns):
                    if btn.collidepoint(e.pos):
                        return diffs[i]


# ─────────────────────────────────────────────────────────────────────────────
# Pawn promotion popup
# ─────────────────────────────────────────────────────────────────────────────
def pawnPromotionPopup(screen, color):
    """color: 'w' or 'b' — whose pawn is promoting."""
    overlay = p.Surface((WINDOW_W, WINDOW_H), p.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 420, 160
    box = p.Rect(WINDOW_W // 2 - box_w // 2, WINDOW_H // 2 - box_h // 2, box_w, box_h)
    p.draw.rect(screen, C_PANEL_BG, box, border_radius=14)
    p.draw.rect(screen, C_PANEL_BORDER, box, 2, border_radius=14)

    title = FONT_STATUS.render("Promote pawn to:", True, C_TEXT_LIGHT)
    screen.blit(title, title.get_rect(centerx=WINDOW_W // 2, y=box.y + 14))

    pieces = ['Q', 'R', 'B', 'N']
    sq = 80
    spacing = 10
    total = len(pieces) * sq + (len(pieces) - 1) * spacing
    start_x = WINDOW_W // 2 - total // 2
    btn_y = box.y + 50

    piece_rects = []
    for i, pc in enumerate(pieces):
        r = p.Rect(start_x + i * (sq + spacing), btn_y, sq, sq)
        piece_rects.append(r)

    clock = p.time.Clock()
    while True:
        mouse = p.mouse.get_pos()
        # Redraw boxes
        for i, (r, pc) in enumerate(zip(piece_rects, pieces)):
            hov = r.collidepoint(mouse)
            bg = (80, 110, 80) if hov else (50, 50, 60)
            p.draw.rect(screen, bg, r, border_radius=8)
            p.draw.rect(screen, C_PANEL_BORDER, r, 2, border_radius=8)
            img_key = color + pc
            if img_key in IMAGES:
                img = p.transform.smoothscale(IMAGES[img_key], (sq - 10, sq - 10))
                screen.blit(img, (r.x + 5, r.y + 5))

        p.display.flip()
        clock.tick(60)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit(); sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for i, r in enumerate(piece_rects):
                    if r.collidepoint(e.pos):
                        return pieces[i]


# ─────────────────────────────────────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────────────────────────────────────
def board_rect(row, col):
    """Return the pygame.Rect for a board square."""
    return p.Rect(BOARD_OFFSET_X + col * SQ_SIZE,
                  BOARD_OFFSET_Y + row * SQ_SIZE,
                  SQ_SIZE, SQ_SIZE)


def draw_board(screen):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = C_LIGHT_SQ if (row + col) % 2 == 0 else C_DARK_SQ
            p.draw.rect(screen, color, board_rect(row, col))


def draw_labels(screen):
    files = "abcdefgh"
    ranks = "87654321"
    for i in range(8):
        # file labels (bottom strip)
        t = FONT_LABEL.render(files[i], True, C_TEXT_DIM)
        x = BOARD_OFFSET_X + i * SQ_SIZE + SQ_SIZE // 2 - t.get_width() // 2
        y = BOARD_OFFSET_Y + BOARD_SIZE + 4
        screen.blit(t, (x, y))
        # rank labels (left strip)
        t = FONT_LABEL.render(ranks[i], True, C_TEXT_DIM)
        x2 = BOARD_OFFSET_X - t.get_width() - 4
        y2 = BOARD_OFFSET_Y + i * SQ_SIZE + SQ_SIZE // 2 - t.get_height() // 2
        screen.blit(t, (x2, y2))


def draw_highlights(screen, gs, validMoves, squareSelected):
    # Last move highlight
    if len(gs.moveLog) > 0:
        last = gs.moveLog[-1]
        for r, c in [(last.startRow, last.startCol), (last.endRow, last.endCol)]:
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s.fill((*C_LAST_MOVE, 130))
            screen.blit(s, board_rect(r, c))

    # King in check
    if gs.inCheck:
        king_loc = gs.whiteKinglocation if gs.whiteToMove else gs.blackKinglocation
        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        s.fill((*C_CHECK, 160))
        screen.blit(s, board_rect(*king_loc))

    if squareSelected != ():
        row, col = squareSelected
        piece = gs.board[row][col]
        if piece != '--' and piece[0] == ('w' if gs.whiteToMove else 'b'):
            # Selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s.fill((*C_HIGHLIGHT, 140))
            screen.blit(s, board_rect(row, col))

            # Possible move dots
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    r, c = move.endRow, move.endCol
                    sq_r = board_rect(r, c)
                    if gs.board[r][c] == '--':
                        # Small dot in centre
                        dot_r = SQ_SIZE // 6
                        cx = sq_r.x + SQ_SIZE // 2
                        cy = sq_r.y + SQ_SIZE // 2
                        circ_surf = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(circ_surf, (*C_POSSIBLE, 170),
                                      (SQ_SIZE // 2, SQ_SIZE // 2), dot_r)
                        screen.blit(circ_surf, sq_r)
                    else:
                        # Capture ring
                        ring_surf = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(ring_surf, (*C_POSSIBLE, 170),
                                      (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 2, 5)
                        screen.blit(ring_surf, sq_r)


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], board_rect(row, col))


# ─────────────────────────────────────────────────────────────────────────────
# Status bar (top)
# ─────────────────────────────────────────────────────────────────────────────
def draw_status_bar(screen, gs, mode, difficulty, ai_thinking):
    bar = p.Rect(0, 0, WINDOW_W, BOARD_OFFSET_Y)
    p.draw.rect(screen, C_PANEL_BG, bar)
    p.draw.line(screen, C_PANEL_BORDER, (0, BOARD_OFFSET_Y - 1), (WINDOW_W, BOARD_OFFSET_Y - 1))

    # Title
    title = FONT_TITLE.render("♟  Chess", True, (220, 220, 240))
    screen.blit(title, (14, 14))

    # Turn indicator
    if not gs.checkmate and not gs.stalemate:
        turn_text = "White to move" if gs.whiteToMove else "Black to move"
        col = C_STATUS_WHITE if gs.whiteToMove else (140, 200, 255)
        t = FONT_STATUS.render(turn_text, True, col)
        screen.blit(t, (BOARD_OFFSET_X + BOARD_SIZE // 2 - t.get_width() // 2 - 60, 20))

    # Difficulty / mode badge
    if mode == "AI":
        badge = f"AI: {difficulty}"
        if ai_thinking:
            badge += "  🤔"
        bt = FONT_STATUS.render(badge, True, (150, 220, 150))
        screen.blit(bt, (WINDOW_W - PANEL_WIDTH - bt.get_width() - 20, 20))


# ─────────────────────────────────────────────────────────────────────────────
# Side panel (move log + buttons)
# ─────────────────────────────────────────────────────────────────────────────
def draw_panel(screen, gs, btn_undo, btn_redo, btn_new, mouse_pos, move_scroll):
    panel_x = BOARD_OFFSET_X + BOARD_SIZE
    panel = p.Rect(panel_x, 0, PANEL_WIDTH, WINDOW_H)
    p.draw.rect(screen, C_PANEL_BG, panel)
    p.draw.line(screen, C_PANEL_BORDER, (panel_x, 0), (panel_x, WINDOW_H), 2)

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = FONT_PANEL.render("Move History", True, C_TEXT_LIGHT)
    screen.blit(hdr, (panel_x + 12, 70))
    p.draw.line(screen, C_PANEL_BORDER,
                (panel_x + 10, 92), (panel_x + PANEL_WIDTH - 10, 92))

    # ── Move list ─────────────────────────────────────────────────────────────
    log_area = p.Rect(panel_x + 2, 98, PANEL_WIDTH - 4, WINDOW_H - 200)
    log_surf  = p.Surface((log_area.width, log_area.height))
    log_surf.fill(C_PANEL_BG)

    moves = gs.moveLog
    pairs = []
    for i in range(0, len(moves), 2):
        w = str(moves[i])
        b = str(moves[i + 1]) if i + 1 < len(moves) else "..."
        pairs.append((i // 2 + 1, w, b))

    row_h    = 22
    visible  = log_area.height // row_h
    # auto-scroll to bottom
    total    = len(pairs)
    start    = max(0, total - visible) if move_scroll < 0 else move_scroll

    for idx, (num, white_m, black_m) in enumerate(pairs[start:start + visible]):
        real_idx = start + idx
        bg = C_MOVE_EVEN if idx % 2 == 0 else C_MOVE_ODD
        # Highlight latest move row
        if real_idx == total - 1:
            bg = C_MOVE_CURRENT
        r = p.Rect(0, idx * row_h, log_area.width, row_h)
        p.draw.rect(log_surf, bg, r)

        num_s  = FONT_MOVE.render(f"{num}.", True, C_TEXT_DIM)
        white_s = FONT_MOVE.render(white_m, True, (220, 220, 220))
        black_s = FONT_MOVE.render(black_m, True, (170, 200, 255))

        log_surf.blit(num_s,  (4,  idx * row_h + 4))
        log_surf.blit(white_s,(36, idx * row_h + 4))
        log_surf.blit(black_s,(130, idx * row_h + 4))

    screen.blit(log_surf, log_area.topleft)

    # ── Buttons ───────────────────────────────────────────────────────────────
    btn_y = WINDOW_H - 105
    hover_undo = btn_undo.collidepoint(mouse_pos)
    hover_redo = btn_redo.collidepoint(mouse_pos)
    hover_new  = btn_new.collidepoint(mouse_pos)

    draw_button(screen, btn_undo, "⟵ Undo (Z)", C_BTN_UNDO, hover=hover_undo)
    draw_button(screen, btn_redo, "Redo (Y) ⟶", C_BTN_REDO, hover=hover_redo)
    draw_button(screen, btn_new,  "New Game (R)", C_BTN_NEW,  hover=hover_new)

    # ── Captured pieces summary ───────────────────────────────────────────────
    draw_captured(screen, gs, panel_x)


def draw_captured(screen, gs, panel_x):
    white_captured = []
    black_captured = []
    for move in gs.moveLog:
        if move.pieceCaptured != '--':
            if move.pieceCaptured[0] == 'w':
                black_captured.append(move.pieceCaptured)
            else:
                white_captured.append(move.pieceCaptured)

    mini = SQ_SIZE // 3
    y = BOARD_OFFSET_Y + BOARD_SIZE - mini - 4
    x = panel_x + 8
    for pc in white_captured[:12]:
        img = p.transform.smoothscale(IMAGES[pc], (mini, mini))
        screen.blit(img, (x, y))
        x += mini + 1
    y -= mini + 4
    x = panel_x + 8
    for pc in black_captured[:12]:
        img = p.transform.smoothscale(IMAGES[pc], (mini, mini))
        screen.blit(img, (x, y))
        x += mini + 1


# ─────────────────────────────────────────────────────────────────────────────
# Move animation
# ─────────────────────────────────────────────────────────────────────────────
def animateMove(move, screen, gs, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames_per_sq = 4
    frame_count = (abs(dR) + abs(dC)) * frames_per_sq

    for frame in range(frame_count + 1):
        t = frame / frame_count if frame_count else 1
        r = move.startRow + dR * t
        c = move.startCol + dC * t

        draw_board(screen)
        draw_highlights(screen, gs, [], ())
        draw_pieces(screen, gs.board)

        # Erase destination square
        color = C_LIGHT_SQ if (move.endRow + move.endCol) % 2 == 0 else C_DARK_SQ
        p.draw.rect(screen, color, board_rect(move.endRow, move.endCol))

        # Draw captured piece if present
        if move.pieceCaptured != '--' and not move.isEnpassantMove:
            screen.blit(IMAGES[move.pieceCaptured], board_rect(move.endRow, move.endCol))

        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved],
                    p.Rect(BOARD_OFFSET_X + c * SQ_SIZE,
                           BOARD_OFFSET_Y + r * SQ_SIZE,
                           SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(240)


# ─────────────────────────────────────────────────────────────────────────────
# End game overlay
# ─────────────────────────────────────────────────────────────────────────────
def draw_end_overlay(screen, text):
    overlay = p.Surface((BOARD_SIZE, BOARD_SIZE), p.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    font_big = p.font.SysFont("Segoe UI", 36, bold=True)
    font_sm  = p.font.SysFont("Segoe UI", 18)

    t1 = font_big.render(text, True, (255, 255, 100))
    t2 = font_sm.render("Press R to play again", True, (200, 200, 200))

    cx = BOARD_OFFSET_X + BOARD_SIZE // 2
    cy = BOARD_OFFSET_Y + BOARD_SIZE // 2
    screen.blit(t1, t1.get_rect(centerx=cx, centery=cy - 20))
    screen.blit(t2, t2.get_rect(centerx=cx, centery=cy + 28))


# ─────────────────────────────────────────────────────────────────────────────
# Sound (graceful fallback if files missing)
# ─────────────────────────────────────────────────────────────────────────────
class SilentSound:
    def play(self): pass

def load_sound(path):
    try:
        return p.mixer.Sound(path)
    except Exception:
        return SilentSound()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    p.init()
    p.mixer.init()

    screen = p.display.set_mode((WINDOW_W, WINDOW_H))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    init_fonts()

    move_sound    = load_sound("sounds/move-sound.mp3")
    capture_sound = load_sound("sounds/capture.mp3")
    promote_sound = load_sound("sounds/promote.mp3")

    # ── Menus ─────────────────────────────────────────────────────────────────
    mode = showModeSelect(screen)          # "AI" or "HUMAN"
    difficulty = "HARD"
    playerWhiteHuman = True
    playerBlackHuman = True

    if mode == "AI":
        difficulty        = showDifficultySelect(screen)
        playerWhiteHuman, playerBlackHuman = showColorSelect(screen)

    # ── Game init ─────────────────────────────────────────────────────────────
    def reset_game():
        gs = GameState()
        if gs.playerWantsToPlayAsBlack:
            gs.board = [row[:] for row in gs.board1]
        return gs, gs.getValidMoves()

    gs, validMoves = reset_game()
    loadImages()

    # Panel button rects
    panel_x   = BOARD_OFFSET_X + BOARD_SIZE
    btn_w, btn_h = PANEL_WIDTH - 24, 34
    btn_undo = p.Rect(panel_x + 12, WINDOW_H - 110, btn_w, btn_h)
    btn_redo = p.Rect(panel_x + 12, WINDOW_H - 72,  btn_w, btn_h)
    btn_new  = p.Rect(panel_x + 12, WINDOW_H - 34,  btn_w, btn_h)

    squareSelected    = ()
    playerClicks      = []
    gameOver          = False
    AIThinking        = False
    moveFinderProcess = None
    moveUndone        = False
    moveMade          = False
    animate           = False
    pieceCaptured     = False
    move_scroll       = -1  # -1 = auto-scroll to bottom
    positionHistory   = ""
    previousPos       = ""
    countMovesForDraw = 0
    COUNT_DRAW        = 0

    end_text = ""
    running = True

    while running:
        mouse_pos = p.mouse.get_pos()
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or \
                    (not gs.whiteToMove and playerBlackHuman)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # ── Mouse ─────────────────────────────────────────────────────────
            elif e.type == p.MOUSEBUTTONDOWN:
                mx, my = e.pos

                # Panel buttons
                if btn_undo.collidepoint(mx, my):
                    gs.undoMove()
                    moveMade = True; animate = False
                    gameOver = False; moveUndone = True
                    end_text = ""
                    if AIThinking and moveFinderProcess:
                        moveFinderProcess.terminate(); AIThinking = False

                elif btn_redo.collidepoint(mx, my):
                    if gs.redoStack:
                        saved_redo = gs.redoStack[:]
                        move_to_redo = saved_redo.pop()
                        gs.makeMove(move_to_redo)
                        gs.redoStack = saved_redo
                        moveMade = True; animate = True
                        gameOver = False; end_text = ""

                elif btn_new.collidepoint(mx, my):
                    gs, validMoves = reset_game()
                    squareSelected = (); playerClicks = []
                    moveMade = False; animate = False
                    gameOver = False; end_text = ""
                    AIThinking = False; moveUndone = True
                    positionHistory = ""; previousPos = ""
                    countMovesForDraw = 0; COUNT_DRAW = 0
                    if moveFinderProcess and moveFinderProcess.is_alive():
                        moveFinderProcess.terminate()

                # Board clicks
                elif not gameOver and humanTurn:
                    col = (mx - BOARD_OFFSET_X) // SQ_SIZE
                    row = (my - BOARD_OFFSET_Y) // SQ_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        if squareSelected == (row, col):
                            squareSelected = (); playerClicks = []
                        else:
                            squareSelected = (row, col)
                            playerClicks.append(squareSelected)

                        if len(playerClicks) == 2:
                            move = Move(playerClicks[0], playerClicks[1], gs.board)
                            for vm in validMoves:
                                if move == vm:
                                    if gs.board[vm.endRow][vm.endCol] != '--':
                                        pieceCaptured = True
                                    gs.makeMove(vm)
                                    if vm.isPawnPromotion:
                                        promo = pawnPromotionPopup(screen, vm.pieceMoved[0])
                                        gs.board[vm.endRow][vm.endCol] = vm.pieceMoved[0] + promo
                                        promote_sound.play(); pieceCaptured = False
                                    if pieceCaptured or vm.isEnpassantMove:
                                        capture_sound.play()
                                    elif not vm.isPawnPromotion:
                                        move_sound.play()
                                    pieceCaptured = False
                                    moveMade = True; animate = True
                                    squareSelected = (); playerClicks = []
                                    break
                            if not moveMade:
                                playerClicks = [squareSelected]

            # ── Keyboard ──────────────────────────────────────────────────────
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True; animate = False
                    gameOver = False; moveUndone = True; end_text = ""
                    if AIThinking and moveFinderProcess:
                        moveFinderProcess.terminate(); AIThinking = False

                elif e.key == p.K_y:
                    if gs.redoStack:
                        saved_redo = gs.redoStack[:]
                        move_to_redo = saved_redo.pop()
                        gs.makeMove(move_to_redo)
                        gs.redoStack = saved_redo
                        moveMade = True; animate = True
                        gameOver = False; end_text = ""

                elif e.key == p.K_r:
                    gs, validMoves = reset_game()
                    squareSelected = (); playerClicks = []
                    moveMade = False; animate = False
                    gameOver = False; end_text = ""
                    AIThinking = False; moveUndone = True
                    positionHistory = ""; previousPos = ""
                    countMovesForDraw = 0; COUNT_DRAW = 0
                    if moveFinderProcess and moveFinderProcess.is_alive():
                        moveFinderProcess.terminate()

        # ── AI turn ───────────────────────────────────────────────────────────
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or \
                    (not gs.whiteToMove and playerBlackHuman)

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(
                    target=findBestMove,
                    args=(gs, validMoves, returnQueue, difficulty))
                moveFinderProcess.start()

            if moveFinderProcess and not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)

                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True

                gs.makeMove(AIMove)

                if AIMove.isPawnPromotion:
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + 'Q'
                    promote_sound.play(); pieceCaptured = False

                if pieceCaptured or AIMove.isEnpassantMove:
                    capture_sound.play()
                elif not AIMove.isPawnPromotion:
                    move_sound.play()

                pieceCaptured = False
                AIThinking    = False
                moveMade      = True
                animate       = True
                squareSelected = (); playerClicks = []

        # ── Post-move ─────────────────────────────────────────────────────────
        if moveMade:
            if countMovesForDraw < 4:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1; positionHistory = ""; countMovesForDraw = 0
                else:
                    previousPos = positionHistory; positionHistory = ""
                    countMovesForDraw = 0; COUNT_DRAW = 0

            if animate and gs.moveLog:
                animateMove(gs.moveLog[-1], screen, gs, clock)
            validMoves  = gs.getValidMoves()
            moveMade    = False
            animate     = False
            moveUndone  = False

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(C_BG)
        draw_status_bar(screen, gs, mode, difficulty, AIThinking)
        draw_board(screen)
        draw_highlights(screen, gs, validMoves, squareSelected)
        draw_pieces(screen, gs.board)
        draw_labels(screen)
        draw_panel(screen, gs, btn_undo, btn_redo, btn_new, mouse_pos, move_scroll)

        # ── End-game check ────────────────────────────────────────────────────
        if COUNT_DRAW >= 1:
            gameOver = True; end_text = "Draw by repetition"
        if gs.stalemate:
            gameOver = True; end_text = "Stalemate"
        elif gs.checkmate:
            gameOver = True
            end_text = "Black wins!" if gs.whiteToMove else "White wins!"

        if gameOver and end_text:
            draw_end_overlay(screen, end_text)

        clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()


if __name__ == "__main__":
    main()